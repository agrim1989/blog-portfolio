# Admin Access Guide

## Admin Login URL
**URL:** http://127.0.0.1:5000/admin/login

## Login Credentials
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Important:** Change the default password in production!

## Admin Features

### Dashboard
- **URL:** http://127.0.0.1:5000/admin/dashboard
- View statistics: Total posts, published posts, drafts, total views
- Quick access to recent posts
- Create new post button

### Manage Blog Posts
- **URL:** http://127.0.0.1:5000/admin/posts
- View all blog posts
- Filter by status: All, Published, Drafts (Hidden/Private)
- Edit, Delete, or View posts

### Create New Post
- **URL:** http://127.0.0.1:5000/admin/posts/new
- Add title, content, featured image
- Upload videos (embedded URL or file upload)
- Set category and tags
- **Status Options:**
  - **Published:** Post is visible to public
  - **Draft:** Post is hidden/private (not visible to public)

### Edit Post
- **URL:** http://127.0.0.1:5000/admin/posts/<id>/edit
- Edit all post details
- Change status (Published ↔ Draft)
- Update images and videos
- Modify content using rich text editor

### Delete Post
- Click "Delete" button in post list
- Confirmation required before deletion
- Permanently removes post from database

## Blog Post Status

### Published
- ✅ Visible on blog homepage
- ✅ Accessible via direct URL
- ✅ Appears in category/tag listings
- ✅ Searchable

### Draft (Hidden/Private)
- ❌ Not visible on blog homepage
- ❌ Not accessible via direct URL
- ❌ Hidden from public view
- ✅ Only visible in admin panel
- ✅ Can be edited and published later

## How to Hide/Private a Post

1. Go to **Admin Dashboard** → **Manage Posts**
2. Click **Edit** on the post you want to hide
3. Change **Status** from "Published" to "Draft"
4. Click **Update Post**
5. Post is now hidden from public view

## How to Make a Post Public

1. Go to **Admin Dashboard** → **Manage Posts**
2. Filter by **Drafts (Hidden/Private)**
3. Click **Edit** on the post
4. Change **Status** from "Draft" to "Published"
5. Click **Update Post**
6. Post is now visible to public

## Quick Actions

### Add New Blog Post
1. Login to admin panel
2. Click "Create New Post" or go to `/admin/posts/new`
3. Fill in the form:
   - Title (required)
   - Content (use rich text editor)
   - Featured Image (optional)
   - Video URL or Video File (optional)
   - Category (optional)
   - Tags (comma-separated)
   - Status: Published or Draft
4. Click "Create Post"

### Delete a Post
1. Go to **Manage Posts**
2. Click **Delete** button
3. Confirm deletion
4. Post is permanently removed

### Edit a Post
1. Go to **Manage Posts**
2. Click **Edit** button
3. Make changes
4. Click "Update Post"

## Admin Access from Website

- **Footer Link:** Click "Admin Login" link in the footer of any page
- **Direct URL:** http://127.0.0.1:5000/admin/login

## Security Notes

- Admin panel requires authentication
- Only logged-in admin users can access admin routes
- All admin actions are protected by login requirement
- Change default password before deploying to production

