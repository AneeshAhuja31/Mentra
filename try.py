from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

hashed = pwd_context.hash("funigga")
print(hashed)
print(pwd_context.verify("funigga",hashed))