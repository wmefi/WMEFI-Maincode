# 🚀 Quick Setup Guide - React Dashboard Integration

## ✅ What Has Been Done

### 1. **Supabase Removed** ✓
- Removed `@supabase/supabase-js` from package.json
- App is now lightweight and SQLite-compatible

### 2. **Django REST API Created** ✓
- Created `wtestapp/api_views.py` with two endpoints:
  - `/api/researchers/` - Returns all doctor/researcher data
  - `/api/dashboard-stats/` - Returns dashboard statistics
- URLs configured in `wtestapp/urls.py`

### 3. **React App Updated** ✓
- App.tsx now fetches real data from Django API
- Added loading states
- Removed mock data dependency

### 4. **Static Files Configured** ✓
- WhiteNoise middleware added for production
- STATICFILES_STORAGE configured
- Static files will be served efficiently on Render

### 5. **CORS Headers Added** ✓
- django-cors-headers installed
- CORS middleware configured
- Allows React dev server to communicate with Django

### 6. **Deployment Ready** ✓
- build.sh script created for Render
- DEPLOYMENT_GUIDE.md with full instructions
- requirements.txt updated

---

## 📝 Next Steps to Use Dashboard

### Local Development:

1. **Install new dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run Django server:**
```bash
python manage.py runserver
```

3. **In another terminal, run React app:**
```bash
cd wtestapp/templates/wtestapp/admin_minidash
npm install
npm run dev
```

4. **Access dashboard at:**
- React dev: `http://localhost:5173`
- Django: `http://127.0.0.1:8000/admin_dashboard/`

---

### Production Deployment on Render:

1. **Commit all changes:**
```bash
git add .
git commit -m "Integrate React dashboard with Django API"
git push origin main
```

2. **In Render Dashboard:**
   - Build Command: `./build.sh`
   - Start Command: `gunicorn wtest.wsgi:application`

3. **Set Environment Variables** (in Render):
```
DEBUG=False
SECRET_KEY=<your-secret-key>
ALLOWED_HOSTS=<your-app>.onrender.com
```

4. **After deployment, build static files:**
React app will be built automatically via build.sh

5. **Access dashboard:**
```
https://your-app.onrender.com/admin_dashboard/
```

---

## 🔧 API Endpoints Available

### Get All Researchers
```
GET /api/researchers/
```
Returns: List of all doctors with survey progress, status, etc.

### Get Dashboard Stats
```
GET /api/dashboard-stats/
```
Returns: Total researchers, completion rates, survey stats

---

## 🎯 What to Expect

### ✅ Working Features:
- Real-time data from your SQLite/MySQL database
- Dashboard shows actual doctors, surveys, progress
- Completion rates calculated automatically
- Search and filter functionality
- Export to CSV

### 📊 Dashboard Sections:
1. **Dashboard** - Overview with metrics
2. **Analytics** - Performance insights (mock data for now)
3. **Researchers** - All researcher cards
4. **Survey Status** - Detailed survey tracking
5. **Schedule** - Calendar view (mock data for now)
6. **Settings** - Export and configuration
7. **Help** - Support resources

---

## 🐛 Troubleshooting

### Issue: API returns empty array
**Check:** Do you have doctors in database?
```bash
python manage.py shell
>>> from wtestapp.models import Doctor
>>> Doctor.objects.count()
```

### Issue: CORS error in development
**Solution:** Make sure django-cors-headers is installed
```bash
pip install django-cors-headers
```

### Issue: Static files not loading in production
**Solution:** Run collectstatic
```bash
python manage.py collectstatic --noinput
```

---

## 📂 File Structure

```
WMEFI-Maincode/
├── wtestapp/
│   ├── api_views.py          # NEW - API endpoints
│   ├── urls.py               # UPDATED - Added API routes
│   ├── views.py              # UPDATED - Dashboard view
│   └── templates/
│       └── wtestapp/
│           ├── admin_minidash/        # React source
│           │   ├── src/
│           │   │   └── App.tsx        # UPDATED - Fetch from API
│           │   ├── package.json       # UPDATED - Removed Supabase
│           │   └── dist/             # Build output (after npm run build)
│           └── admin_minidash_view.html  # NEW - Django template
├── wtest/
│   └── settings.py           # UPDATED - WhiteNoise, CORS
├── requirements.txt          # UPDATED - Added django-cors-headers
├── build.sh                  # NEW - Render build script
├── DEPLOYMENT_GUIDE.md       # NEW - Full deployment guide
└── QUICK_SETUP.md           # THIS FILE
```

---

## 🎉 Summary

Your React dashboard is now **fully integrated** with Django backend:

✅ Uses real database data (no more mock data)  
✅ Production-ready with WhiteNoise  
✅ Render deployment configured  
✅ No Supabase dependency  
✅ CORS configured for development  
✅ Loading states added  
✅ API endpoints documented  

**Ready to deploy on Render!** 🚀
