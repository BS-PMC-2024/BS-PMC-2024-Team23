from main import app, db, Users

with app.app_context():

    # יצירת משתמש Admin
    admin_user = Users(
        user_type="Admin",
        first_name="Admin",
        last_name="User",
        email="admin@admin.com",
        password="1",
        age=30,
        weight=70.0,
        height=175.0
    )

    # הוספת אדמין למסד הנתונים
    db.session.add(admin_user)
    db.session.commit()

    print("Admin user added successfully!")
