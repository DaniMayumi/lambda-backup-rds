import os
import json
import boto3
import subprocess
import datetime
from zoneinfo import ZoneInfo

# ENVIRONMENT VARIABLES
DB_HOST = os.getenv("DB_HOST", "postgres11-teste.csrqpahbegrw.us-east-1.rds.amazonaws.com")
DB_PORT = os.getenv("DB_PORT", "5432")
SECRET_ARN = os.getenv("SECRET_ARN", "arn:aws:secretsmanager:us-east-1:909203251240:secret:secret-rds-postgres11-SylFbC")  
S3_BUCKET = os.getenv("S3_BUCKET", "backup-teste-lambda")
S3_PREFIX = os.getenv("S3_PREFIX", "postgres/")

s3_client = boto3.client("s3")
secrets_client = boto3.client("secretsmanager")

def get_db_credentials(secret_arn):
    """Recupera usuário e senha do Secrets Manager"""
    response = secrets_client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response["SecretString"])
    return secret["username"], secret["password"]

def list_databases(db_user, db_password):
    """Lista bancos de dados (exceto templates e rdsadmin)"""
    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    cmd = [
        "psql",
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", db_user,
        "-d", "postgres",
        "-t",  # no headers
        "-c", """
        SELECT datname
        FROM pg_database
        WHERE datistemplate = false
          AND datname NOT IN ('rdsadmin');  
        """
    ]

    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"psql failed: {result.stderr}")
    
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]

def backup_database(db, db_user, db_password, timestamp):
    """Executa pg_dump de um banco e faz upload pro S3"""
    filename = f"{db}_{timestamp}.dump"
    filepath = f"/tmp/{filename}"

    dump_cmd = [
        "pg_dump",
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", db_user,
        "-d", db,
        "-f", filepath
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    subprocess.check_call(dump_cmd, env=env)
