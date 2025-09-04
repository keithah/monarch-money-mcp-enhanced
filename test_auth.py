#!/usr/bin/env python3
"""Test Monarch Money authentication"""

import asyncio
import os
from monarchmoney import MonarchMoney

async def test_auth():
    mm = MonarchMoney()
    
    email = os.getenv("MONARCH_EMAIL")
    password = os.getenv("MONARCH_PASSWORD") 
    mfa_secret = os.getenv("MONARCH_MFA_SECRET")
    
    print(f"Testing auth with email: {email}")
    print(f"MFA secret length: {len(mfa_secret) if mfa_secret else 0}")
    
    try:
        if mfa_secret:
            print("Attempting login with MFA...")
            await mm.login(email, password, mfa_secret_key=mfa_secret)
        else:
            print("Attempting login without MFA...")
            await mm.login(email, password)
        
        print("✅ Login successful!")
        
        # Test a simple API call
        accounts = await mm.get_accounts()
        print(f"✅ Got {len(accounts)} accounts")
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_auth())