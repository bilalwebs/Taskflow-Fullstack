---
name: frontend-skill
description: Build frontend interfaces including pages, reusable components, layouts, and styling systems.
---

# Frontend Skill

## Instructions

1. **Page Building**
   - Create application pages based on requirements
   - Structure pages with semantic HTML
   - Handle routing and navigation
   - Optimize for performance and SEO

2. **Component Design**
   - Build reusable and composable components
   - Follow single-responsibility principle
   - Pass data via props or state
   - Maintain component consistency

3. **Layout Structure**
   - Design responsive layouts
   - Use Flexbox and Grid effectively
   - Implement headers, footers, and sidebars
   - Ensure mobile-first design

4. **Styling**
   - Apply consistent design systems
   - Use CSS, Tailwind, or component libraries
   - Manage global vs local styles
   - Support light and dark themes

5. **UI State Handling**
   - Handle loading, error, and empty states
   - Manage user interactions
   - Ensure accessibility standards (a11y)

## Best Practices
- Keep components small and reusable
- Use consistent spacing and typography
- Design mobile-first, then scale up
- Follow accessibility guidelines (ARIA, contrast)
- Avoid inline styles for large components
- Test UI across devices and screen sizes

## Example Structure
```tsx
// Pages
/pages
  ├─ index.tsx
  ├─ dashboard.tsx

// Components
/components
  ├─ Button.tsx
  ├─ Card.tsx
  ├─ Layout.tsx

// Layout Flow
Page → Layout → Components → Styles
