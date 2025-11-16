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
   - create a user.

   - send verification email.

   - return user info.



   #### 2.log in
    - email + password.

    - return JWT tokens.

    - block unverified users.



   #### 3.Me/profile endpoint
     - returns logged in user info


    #### 4.logout

###
 1. Session Auth
 2. JWT Auth

    - Access tokens.
    - refresh token.
    - stateless auth
    - works better for mobile/web/external clients
    - can be stored in http-only cookie/headers
    - reduces server memory load
    

    ```bash
    pip install djangorestframework-simplejwt

    ```

    ### Signup serializer
       + validate input
       + create user
       + hash password
       + not log uer automatically
       + return email and is_verified

    #### registration decisions
       1. required sign-up fields ie email + password +optional names
       2. signup automatically log user in OR vice versa
         
       + accept input/validate 

       + create user 

        <pre>User.objects.create_user(...)</pre>

        + issue jwt immediately(generate tokens)

        <pre>RefreshToken.for_user(user)</pre>

        + return user data + tokens
          <pre>
          {
            "email":
            "is_verified":
            "access":
            "refresh":
          }
          </pre>


## views
  1. accept POST/api/accounts/signup/ with email + password
  2. validate input via SignUpSerializer
  3. create the user via the serializer which calls UserManager
  4. returns 201 created with {email, is_verified,access, refresh}
  5. return meaningful errors (400), 500 etc

  + the view decides how to request data
  + which serializer to use 
  + whether the data is valid
  + how to call our UserManager & Serializer logic
  + what response to send back
  + what status code to return

  custom methodsobject is request and response
  
### API TESTING WITH CURL
  
  ```bash
  curl - tool to send HTTP reqs

  -X POST - this is a post request

  URL - ie signup url endpoint

  -H - header (telling django its JSON)

  -d - request body (JSON data)

  ```
  ```bash
  curl -X POST \
  http://127.0.0.1:8000/api/accounts/signup/ \
  -H "Content-Type: application/json" \
  -d '{
        "email": "me@gmail.com",
        "password": "Chicha1960",
        "first_name": "kaila"
      }'
```

