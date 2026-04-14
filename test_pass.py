import bcrypt

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

hashed = "$2b$12$xfrSzRdbI1o/PDOxOs3bFexVbDDU7lfmoXi7dojEAooIF0wpieFpW"
print(f"admin123: {verify_password('admin123', hashed)}")
print(f"admin: {verify_password('admin', hashed)}")
