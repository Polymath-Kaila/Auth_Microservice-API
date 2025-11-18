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

  custom methodsobject   "email": "kailaevans@gmail.com",
  "is_verified": false,is request and response
  
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
### FLOW
   1. Frontend sends a POST JSON
   2. URL router sees /account/signup/
   3. Django calls SignupView.post()
   4. we create a serializer with req.data
   5. serializer.is_valid() checks rules
   6. serializer.save()- triggers creat()
   7. create() uses UserManager.create_user()
   8. user gets stored in DB 
   9. View returns JSON res 
   10. fronted receives success + tokens


### LOGIN
its to:
+ validate email and password
+ authenticate the user
+ block login if email is wrong
+ block login if password is wrong
+ block login if user is not verified 
+ generate access + refresh tokens
+ return to user


### LOGOUT with refresh tokens blacklist
+ onlogout, the client sends the refresh token.
+ the server marks this refresh token as `blacklist`
+ Any future attempts to refresh with this token are rejected
+ The user effectively becomes logged out

- blacklisted tokens are stoed in a cache system ie redis

#### /logout/ endpoint
1. client sends `refresh token`
2. validate it
3. Extract token jti(unique ID)
4. Save jti into redis
5. later if refresh is used --.check if redis -->deny

+ we first install redis conn from django 
 ```bash
 pip install redis
 ```
+ we cofigure in settings.py 


### Email verification 
  + user signs up, is_verified=false, no otp yet
  + fronted calls /send-otp/
  + backend :
  1. gen 6 digit otp
  2. store it temporarily
  3. send it via email
  4. bind otp to user email/user_id
  5. send an expiry 5-10 mins
  + user enters otp in frontend--> fronted calls /verify-email/
  + backend verifys otp
  1. check if otp exists
  2. check if it matches
  3. check if not expired
  4. check if not already used
  5. make user_is_verified = true
  6. delete/expire the OTP


