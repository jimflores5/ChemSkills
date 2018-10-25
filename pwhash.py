import hashlib, random, string

def make_salt():    #Generates a sting of 5 random characters to add to the hashed password.
    salt = ''.join([random.choice(string.ascii_letters) for x in range(5)])
    return salt

def make_pw_hash(password, salt=None):    #Takes the registration password, adds the 'salt' and then hashes the result.
    if not salt:    #1st time registration generates a salt.  Login of current users retrieves past salt from DB.
        salt = make_salt()
    hash = hashlib.sha256(str.encode(password + salt)).hexdigest()
    return '{0}_{1}'.format(hash, salt)    #The password and salt hashes are separated by the '_' character and will be stored as 1 entry in the database.

def check_pw_hash(password, hash):
    salt = hash.split('_')[1]    #Separates the password and salt characters from the 'hash' entry in the database.
    if make_pw_hash(password, salt) == hash:  #Hashes current password attempt, combines it with salt retireved from DB, and then compares the result with the stored pw hash+salt.
        return True

    return False