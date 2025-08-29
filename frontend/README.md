# File Collaboration Frontend

A Vue.js frontend for the File Collaboration Platform with authentication and file management features.

## Features

- 🔐 User authentication (login/register)
- 📁 File management (create, read, update, delete)
- 🎨 Modern UI with Tailwind CSS
- 📱 Responsive design
- 🔒 Protected routes with authentication guards
- 💾 Persistent authentication state

## Tech Stack

- **Vue 3** - Progressive JavaScript framework
- **Vue Router** - Official router for Vue.js
- **Pinia** - State management for Vue
- **Axios** - HTTP client for API requests
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Build tool and dev server

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

## API Configuration

The frontend is configured to proxy API requests to your backend at `http://localhost:8000`. Make sure your backend is running and CORS is properly configured.

## Project Structure

```
src/
├── components/          # Reusable Vue components
├── views/              # Page components
│   ├── Home.vue        # Dashboard page
│   ├── Login.vue       # Login form
│   ├── Register.vue    # Registration form
│   └── Files.vue       # File management page
├── stores/             # Pinia stores
│   └── auth.js         # Authentication store
├── services/           # API services
│   └── api.js          # HTTP client and API methods
├── router/             # Vue Router configuration
│   └── index.js        # Route definitions and guards
├── App.vue             # Root component
└── main.js             # Application entry point
```

## Authentication Flow

1. **Registration**: Users can create new accounts with email, password, and full name
2. **Login**: Users authenticate with email and password to receive JWT tokens
3. **Token Storage**: JWT tokens are stored in localStorage for persistent sessions
4. **Route Protection**: Protected routes automatically redirect to login if not authenticated
5. **Auto-logout**: Expired or invalid tokens automatically log out users

## File Management

- **Create**: Add new files with filename and content
- **View**: Display file content in a modal
- **Edit**: Update existing file content
- **Delete**: Remove files with confirmation
- **List**: View all user files with preview

## Development

### Adding New Features

1. Create new components in `src/components/`
2. Add new views in `src/views/`
3. Update router configuration in `src/router/index.js`
4. Add API methods in `src/services/api.js` if needed

### Styling

The project uses Tailwind CSS for styling. Custom styles can be added in `src/style.css`.

### State Management

Use Pinia stores for global state management. The authentication store is already set up in `src/stores/auth.js`.
