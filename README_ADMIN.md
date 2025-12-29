# Admin Panel Quick Start Guide

## 🔐 Admin Login

**URL:** http://127.0.0.1:5000/admin/login

**Credentials:**
- Username: `admin`
- Password: `admin123`

## 📝 Quick Access Links

- **Admin Login:** http://127.0.0.1:5000/admin/login
- **Dashboard:** http://127.0.0.1:5000/admin/dashboard
- **Manage Posts:** http://127.0.0.1:5000/admin/posts
- **Create Post:** http://127.0.0.1:5000/admin/posts/new

## ✨ Key Features

### Blog Post Management

1. **Create New Post**
   - Click "Create New Post" button
   - Fill in title, content, images, videos
   - Set status: **Published** (public) or **Draft** (hidden/private)
   - Add categories and tags

2. **Edit Post**
   - Go to "Manage Posts"
   - Click "Edit" on any post
   - Modify content, images, status
   - Change from Published to Draft to hide it

3. **Delete Post**
   - Click "Delete" button
   - Confirm deletion
   - Post is permanently removed

4. **Hide/Private Post**
   - Edit the post
   - Change status from "Published" to "Draft"
   - Save - post is now hidden from public

5. **Make Post Public**
   - Edit a draft post
   - Change status from "Draft" to "Published"
   - Save - post is now visible

## 📊 Post Status Explained

- **Published:** ✅ Visible on blog, searchable, accessible via URL
- **Draft:** ❌ Hidden from public, only visible in admin panel

## 🖼️ Upload Profile Image

Your profile image has been uploaded! It will appear on:
- Homepage hero section
- Resume page header

To change it:
1. Login to admin
2. Upload new image through admin interface
3. Or use: `python3 upload_profile_image.py <image_file>`

## 📱 Responsive Design

All pages are fully responsive and work on:
- Desktop (1200px+)
- Tablet (768px - 1024px)
- Mobile (320px - 768px)

## 🔗 Access from Website

- **Footer:** Click "Admin Login" link at bottom of any page
- **Direct URL:** Type `/admin/login` in browser

## ⚠️ Security Note

Change the default password before deploying to production!

