import sqlite3

conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

cursor.execute("SELECT id, email FROM users WHERE email LIKE '%alinebierr%'")
user = cursor.fetchone()
if not user:
    print('User not found')
    exit()

user_id = user[0]
print(f'Injecting mock data for user {user[1]} (ID: {user_id})')

# Insert Patient Profile
cursor.execute('DELETE FROM patient_profiles WHERE user_id = ?', (user_id,))
cursor.execute("INSERT INTO patient_profiles (id, user_id, age, gender, height, weight, blood_type) VALUES (lower(hex(randomblob(16))), ?, '28', 'Erkek', '180', '85', 'A+')", (user_id,))

# Insert Conditions
cursor.execute('DELETE FROM patient_conditions WHERE user_id = ?', (user_id,))
cursor.execute("INSERT INTO patient_conditions (user_id, condition_name, diagnosed_date) VALUES (?, 'Hipertansiyon', '2020-01-01')", (user_id,))
cursor.execute("INSERT INTO patient_conditions (user_id, condition_name, diagnosed_date) VALUES (?, 'Astım', '2015-06-01')", (user_id,))

# Insert Allergies
cursor.execute('DELETE FROM patient_allergies WHERE user_id = ?', (user_id,))
cursor.execute("INSERT INTO patient_allergies (user_id, allergen_name, reaction_severity) VALUES (?, 'Penisilin', 'Yüksek')", (user_id,))
cursor.execute("INSERT INTO patient_allergies (user_id, allergen_name, reaction_severity) VALUES (?, 'Polen', 'Orta')", (user_id,))

conn.commit()
conn.close()
print('Data injected successfully via raw SQL!')
