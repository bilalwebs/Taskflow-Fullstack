# Frontend - Next.js Todo Application

Modern, responsive web interface for the KIro Todo application with Better Auth integration.

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.local.example .env.local
```

Edit `.env.local` and set:
- `NEXT_PUBLIC_API_URL`: Backend API URL (http://localhost:8000)
- `BETTER_AUTH_SECRET`: Same secret as backend JWT_SECRET
- `BETTER_AUTH_URL`: Frontend URL (http://localhost:3000)

### 3. Start Development Server

```bash
npm run dev
```

Application runs at: http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Landing page
│   │   ├── signup/
│   │   │   └── page.tsx      # Signup page
│   │   ├── signin/
│   │   │   └── page.tsx      # Signin page
│   │   └── dashboard/
│   │       └── page.tsx      # Task dashboard
│   ├── components/
│   │   ├── AuthForm.tsx      # Auth form component
│   │   ├── TaskList.tsx      # Task list display
│   │   ├── TaskItem.tsx      # Individual task
│   │   └── TaskForm.tsx      # Task create/edit form
│   ├── lib/
│   │   ├── auth.ts           # Better Auth config
│   │   ├── api-client.ts     # API client with JWT
│   │   └── types.ts          # TypeScript types
│   └── styles/
│       └── globals.css       # Global styles
├── public/
├── tests/
├── package.json
├── tsconfig.json
├── next.config.js
└── README.md
```

## Pages

### Landing Page (/)
- Welcome message
- Navigation to signup/signin

### Signup (/signup)
- Create new account
- Email and password validation
- Password strength requirements

### Signin (/signin)
- Sign in with credentials
- Error handling for invalid credentials

### Dashboard (/dashboard)
- View all tasks
- Create new tasks
- Edit existing tasks
- Delete tasks
- Mark tasks complete/incomplete

## Development

### Run Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
npm start
```

### Run Tests
```bash
npm test
```

### Lint Code
```bash
npm run lint
```

## Features

- **Server Components**: Fast initial page loads
- **Client Components**: Interactive UI elements
- **Better Auth**: Secure JWT-based authentication
- **Responsive Design**: Works on mobile and desktop
- **Loading States**: Feedback during API operations
- **Error Handling**: Clear error messages
- **Empty States**: Helpful messages when no tasks

## Styling

Uses Tailwind CSS for responsive design:
- Mobile: 320px+
- Tablet: 768px+
- Desktop: 1024px+
- Large: 1920px+

## Troubleshooting

**Cannot connect to backend:**
- Verify NEXT_PUBLIC_API_URL in .env.local
- Check backend is running on port 8000
- Check CORS configuration in backend

**Authentication not working:**
- Ensure BETTER_AUTH_SECRET matches backend
- Check JWT token in browser DevTools
- Verify token is sent in Authorization header

**Build errors:**
- Delete .next folder and rebuild
- Clear node_modules and reinstall
- Check TypeScript errors with `npm run type-check`
