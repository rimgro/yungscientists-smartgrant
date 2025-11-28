**grant program**
1. id
2. stages (ordered) (one to many)
3. grant_reciever

**stage:**
1. id
2. order
3. amount
4. requirements (one to many)
5. description
6. complete?

**requirement:**
1. id
2. name
3. description
4. complete?

**user:**
1. id
2. name
3. email
4. hashed_password
5. bank_id

**user_to_grant:**
1. user
2. grant
3. roles {grantor, supervisor, grantee}