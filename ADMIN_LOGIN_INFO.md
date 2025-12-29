# Admin Login Information

## 🔐 Login Credentials

**URL:** http://127.0.0.1:5000/admin/login

- **Username:** `admin`
- **Password:** `admin123`

## ✅ Password Reset

If the password doesn't work, run this command to reset it:

```bash
python3 reset_admin_password.py
```

This will reset the admin password to `admin123`.

## 🔑 Quick Access

1. **Direct URL:** http://127.0.0.1:5000/admin/login
2. **From Website Footer:** Click "Admin Login" link at the bottom of any page

## 📋 Admin Features

### Dashboard
- View statistics (total posts, published, drafts, views)
- Quick access to recent posts
- Create new post button

### Manage Posts
- View all blog posts
- Filter by status (All, Published, Drafts)
- Edit, Delete, or View posts
- **Hide/Private:** Change status to "Draft" to hide from public
- **Show:** Change status to "Published" to make visible

### Create/Edit Posts
- Rich text editor (TinyMCE)
- Upload featured images
- Add videos (URL or file upload)
- Set categories and tags
- Control visibility (Published = public, Draft = hidden)

## 🛠️ Troubleshooting

### Password Not Working?

1. Run: `python3 reset_admin_password.py`
2. Try logging in again with:
   - Username: `admin`
   - Password: `admin123`

### Can't Access Admin?

1. Make sure Flask app is running: `python3 app.py`
2. Check the URL: http://127.0.0.1:5000/admin/login
3. Clear browser cache and cookies
4. Try incognito/private browsing mode

### Forgot Password?

Run the reset script:
```bash
python3 reset_admin_password.py
```

## 📱 Responsive Design

All admin pages are fully responsive:
- **Desktop:** Full table view with all columns
- **Tablet:** Optimized layout
- **Mobile:** Card-based view with stacked information

## 🔒 Security Note

⚠️ **Important:** Change the default password before deploying to production!

To change password, edit `reset_admin_password.py` and modify the password, then run it.

