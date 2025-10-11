# React Dashboard Deployment Guide for Render

## 📋 Prerequisites

1. GitHub repository connected to Render
2. PostgreSQL/MySQL database configured on Render
3. Environment variables set

## 🚀 Render Configuration

### Build Command
```bash
./build.sh
```

### Start Command
```bash
gunicorn wtest.wsgi:application
```

## 🔧 Environment Variables (Set in Render Dashboard)

```
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=your-database-url

# Database (if not using DATABASE_URL)
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=3306
```

## 📝 Local Development Setup

### 1. Install Dependencies

**Python:**
```bash
pip install -r requirements.txt
```

**React (for dashboard):**
```bash
cd wtestapp/templates/wtestapp/admin_minidash
npm install
```

### 2. Run Development Servers

**Django Backend:**
```bash
python manage.py runserver
```

**React Dashboard (separate terminal):**
```bash
cd wtestapp/templates/wtestapp/admin_minidash
npm run dev
```
React will run on `http://localhost:5173`

### 3. Build for Production

**Build React app:**
```bash
cd wtestapp/templates/wtestapp/admin_minidash
npm run build
```

**Collect Django static files:**
```bash
python manage.py collectstatic
```

## 🔄 API Endpoints

The React dashboard uses these Django API endpoints:

- `/api/researchers/` - Get all researchers data
- `/api/dashboard-stats/` - Get dashboard statistics

## 📦 What Gets Deployed

### Files Included:
- ✅ Django backend code
- ✅ React build output (`dist/` folder)
- ✅ Static files
- ✅ Database migrations

### Files Excluded (in .gitignore):
- ❌ `node_modules/`
- ❌ `venv/`
- ❌ `__pycache__/`
- ❌ `.env` files

## 🛠️ Troubleshooting

### Issue: Static files not loading
**Solution:** Run `python manage.py collectstatic --noinput`

### Issue: API calls failing
**Solution:** Check CORS settings in `settings.py`

### Issue: Build fails on Render
**Solution:** 
1. Check `build.sh` has execute permissions
2. Verify all dependencies in `requirements.txt`
3. Check Node.js version compatibility

### Issue: Database connection error
**Solution:** Verify environment variables for database configuration

## 🎯 Production Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up SSL/HTTPS
- [ ] Remove Supabase dependency (✅ Done)
- [ ] Test all API endpoints
- [ ] Run migrations on production database

## 📱 Accessing the Dashboard

After deployment, access the React dashboard at:
```
https://your-app-name.onrender.com/admin_dashboard/
```

## 🔐 Security Notes

1. Never commit `.env` files
2. Use environment variables for sensitive data
3. Keep `SECRET_KEY` secure
4. Use HTTPS in production
5. Review CORS settings for production domains

## 📚 Additional Resources

- [Render Django Deployment Guide](https://render.com/docs/deploy-django)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)
- [Vite Build Guide](https://vitejs.dev/guide/build.html)
