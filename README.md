- create project by ruunung
```bash
python manage.py startapp accounts
```

## AbstractBaseUser for custom user model
it has three core pieces

### The user model itself
we define:
1. email
2. optional names
3. status fields ie( is_active,is_staff)
4. verification filed (is_verified)
5. date_joined
6. objects pointing to our custom manager
7. Username_field = "email"

### The UserManager
this controls:
+ how users are created(creat_user)
+ how superusers are created(create_superuser)
+ validation rules
+ normalization of email

### Update settings.py
 ```bash
 AUTH_USER_MODEL = "accounts.User"
 ```
--------------------------------------------------

### User class
- email is used as auto increament ID as Pk.

- email is only used as a unique idetifier fro login 
+ user logs in with email 
+ db stays stable
+ user can change email safety 
+ FKs stay integer and fast
+ compatibiliy stays perfect

-----------------------------------------------------

### API Structure (4 core auth service)

   #### 1.sign up
   - create a user
   - send verification email
   - return user info



   #### 2.log in
    - email + password
    - return JWT tokens
    - block unverified users


   #### 3.Me/profile endpoint
     - returns logged in user info


    #### 4.logout

# Auth_Microservice-API
