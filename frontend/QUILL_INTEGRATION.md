# Quill Editor Integration

This project now uses Quill as the rich text editor for file content creation and editing.

## Features

- **Rich Text Editing**: Full-featured text editor with formatting options
- **Toolbar**: Includes formatting tools like bold, italic, underline, lists, headers, colors, and more
- **HTML Output**: Content is stored as HTML, allowing for rich formatting
- **Responsive Design**: Editor adapts to different screen sizes
- **Vue 3 Integration**: Built with Vue 3 Composition API

## Components

### QuillEditor.vue
A reusable Vue component that wraps the Quill editor with the following features:

- **Props**:
  - `modelValue`: The content value (v-model compatible)
  - `placeholder`: Placeholder text when editor is empty
  - `readOnly`: Whether the editor is read-only
  - `height`: Height of the editor (default: 300px)

- **Events**:
  - `update:modelValue`: Emitted when content changes

## Usage

The Quill editor is integrated into the Files.vue component for:
- Creating new files with rich content
- Editing existing files with formatting preserved
- Viewing files with HTML content rendered

## Toolbar Features

The editor includes the following formatting options:
- **Text Formatting**: Bold, italic, underline, strike-through
- **Headers**: Multiple header levels (H1-H6)
- **Lists**: Ordered and unordered lists
- **Alignment**: Text alignment options
- **Colors**: Text and background colors
- **Fonts**: Font family selection
- **Links & Images**: Insert links and images
- **Code**: Code blocks and inline code
- **Quotes**: Blockquotes
- **Indentation**: Text indentation controls

## Styling

The editor is styled to match the application's design system using Tailwind CSS classes and custom CSS for Quill-specific elements.

## Dependencies

- `quill`: The core Quill editor library
- `vue-quill-editor`: Vue wrapper for Quill (though we created our own custom wrapper for better Vue 3 integration)
