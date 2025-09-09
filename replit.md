# Overview

This is a full-stack food analysis application that uses AI to identify food items in meal photos and classify them by dietary preferences (vegan, vegetarian, meat). The application features an intuitive drag-and-drop interface for image uploads and provides detailed analysis results with confidence scores and visual positioning.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture

The client is built as a React single-page application using modern tooling:

- **Framework**: React with TypeScript and Vite for fast development and building
- **UI Components**: Comprehensive shadcn/ui component library built on Radix UI primitives
- **Styling**: Tailwind CSS with custom design tokens and CSS variables for theming
- **State Management**: TanStack Query (React Query) for server state management and API caching
- **Routing**: Wouter for lightweight client-side routing
- **Forms**: React Hook Form with Zod validation for type-safe form handling

The frontend follows a component-based architecture with reusable UI components, custom hooks, and centralized API handling. The drag-and-drop image upload interface provides immediate visual feedback and supports multiple input methods.

## Backend Architecture

The server is built with Express.js and follows a RESTful API design:

- **Framework**: Express.js with TypeScript for type safety
- **API Structure**: RESTful endpoints with centralized route registration
- **Validation**: Zod schemas shared between client and server for consistent data validation
- **Error Handling**: Centralized error middleware with structured error responses
- **Development**: Hot reloading with Vite integration in development mode

The backend uses a service-oriented architecture where business logic is separated into dedicated service classes, making the codebase maintainable and testable.

## Data Storage Solutions

The application uses multiple storage approaches:

- **Database**: PostgreSQL with Drizzle ORM for type-safe database operations
- **Schema Management**: Centralized schema definitions in the shared directory
- **Development Storage**: In-memory storage implementation for rapid prototyping
- **Migrations**: Drizzle Kit for database schema migrations and version control

The storage layer uses an interface-based design pattern, allowing easy switching between different storage implementations.

## Authentication and Authorization

Currently implements a basic user management system:

- **User Storage**: Interface-based storage with memory implementation
- **Session Management**: Express sessions with PostgreSQL session store (connect-pg-simple)
- **User Operations**: CRUD operations for user management with UUID-based identification

## External Dependencies

### AI and Image Processing

- **OpenAI GPT-5**: Primary AI model for food identification and dietary classification
- **Image Processing**: Base64 image encoding for secure server-side processing
- **Analysis Features**: 
  - Food item identification with confidence scores
  - Dietary classification (vegan/vegetarian/meat)
  - Spatial positioning of identified items in images

### Database and Infrastructure

- **PostgreSQL**: Primary database with Neon serverless hosting
- **Drizzle ORM**: Type-safe database toolkit with PostgreSQL dialect
- **Session Storage**: PostgreSQL-backed session management for scalability

### Development and Build Tools

- **Vite**: Frontend build tool and development server with React plugin
- **ESBuild**: Fast JavaScript bundler for server-side code compilation
- **TypeScript**: Full-stack type safety with shared type definitions
- **Tailwind CSS**: Utility-first CSS framework with PostCSS processing

### UI and Styling Dependencies

- **Radix UI**: Accessible component primitives for complex UI interactions
- **Lucide React**: Comprehensive icon library with consistent styling
- **Class Variance Authority**: Type-safe CSS class composition for component variants
- **Date-fns**: Lightweight date manipulation library for temporal data handling

The application architecture prioritizes type safety, developer experience, and scalable patterns while maintaining a clear separation of concerns between the client, server, and shared utilities.