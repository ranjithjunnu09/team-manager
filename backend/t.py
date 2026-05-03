from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

result = pwd.verify(
    "Password@123",
    "$2b$12$lB25C84LloRdV3tufuuM1etIZNrfEcMwPNaDg2Om/D2eKoMOomsgS"
)

print("✅ Password matches!" if result else "❌ Password does NOT match")