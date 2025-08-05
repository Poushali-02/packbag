# WherYouGo Frontend - React + Vite

A modern frontend for the WherYouGo travel social platform, built with React and Vite, consuming Django REST API endpoints.

## 🚀 Features

- **Modern Feed Interface**: Clean, responsive feed with infinite scroll
- **Post Creation**: Rich post creation with image uploads and tagging
- **Real-time Interactions**: Like, favorite, and comment on posts
- **Search & Discovery**: Search posts by content, tags, and location
- **User Suggestions**: Discover new travelers to follow
- **Responsive Design**: Works beautifully on desktop and mobile
- **Tailwind CSS**: Modern styling with utility-first approach

## 📦 Installation

1. **Install Dependencies**
   ```bash
   cd ui-packbag
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Make sure Django backend is running**
   ```bash
   cd ../wheryougo
   python manage.py runserver
   ```

## 🏗️ Project Structure

```
ui-packbag/src/
├── Components/
│   ├── Feed.jsx              # Main feed component
│   ├── PostCard.jsx          # Individual post display
│   ├── CreatePost.jsx        # Post creation modal
│   ├── SearchBar.jsx         # Search functionality
│   └── SuggestedUsers.jsx    # User suggestions sidebar
├── services/
│   └── feedAPI.js            # API service layer
├── contexts/
│   └── AuthContext.jsx       # Authentication context
├── App.jsx                   # Main app component
└── main.jsx                  # App entry point
```

## 🔧 API Integration

The frontend communicates with Django backend through these endpoints:

### Core Endpoints
- `GET /feed/api/feed/` - Get main feed
- `POST /feed/api/posts/create/` - Create new post
- `GET /feed/api/posts/{id}/` - Get single post
- `POST /feed/api/posts/{id}/like/` - Toggle like
- `POST /feed/api/posts/{id}/favorite/` - Toggle favorite
- `POST /feed/api/posts/{id}/comment/` - Add comment

### Utility Endpoints
- `GET /feed/api/tags/suggestions/` - Get tag suggestions
- `GET /feed/api/posts/search/` - Search posts
- `GET /feed/api/users/{id}/posts/` - Get user posts

## 🎯 Ready to Use!

The frontend is now fully integrated with your Django backend. Start the development server and enjoy building the next great travel social platform!+ Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
