# UI/UX Design Framework for Web Applications

A comprehensive design guide for creating professional, user-friendly web applications and Streamlit dashboards. Use this framework to ensure consistency, usability, and visual appeal across your projects.

---

## 🎨 Design Philosophy

### Core Principles
1. **Clarity Over Complexity** - Simple, intuitive interfaces
2. **Consistency** - Uniform patterns across all pages
3. **Feedback** - Clear response to user actions
4. **Efficiency** - Minimize clicks and cognitive load
5. **Accessibility** - Usable by everyone
6. **Performance** - Fast, responsive interactions

---

## 📐 1. Layout & Structure

### 1.1 Page Layout Patterns

**Dashboard Layout:**
```
┌─────────────────────────────────────────┐
│  Header (Optional)                      │
├──────────┬──────────────────────────────┤
│          │                              │
│ Sidebar  │  Main Content Area           │
│          │                              │
│ Controls │  - Tabs                      │
│ Settings │  - Charts/Data               │
│ Filters  │  - Tables                    │
│          │                              │
└──────────┴──────────────────────────────┘
```

**Content Layout Patterns:**
- **Single Column**: Full-width content (reports, articles)
- **Two Column**: Sidebar + content (dashboards)
- **Three Column**: Navigation + content + sidebar (complex apps)
- **Grid**: Equal-sized cards (galleries, portfolios)
- **Multi-Timeframe**: Horizontal rows of related content

### 1.2 Spacing & Rhythm

**Spacing Scale (8px base):**
```
XXS: 4px   - Tight spacing (icon + text)
XS:  8px   - Compact spacing (form elements)
S:   16px  - Standard spacing (paragraphs)
M:   24px  - Section spacing
L:   32px  - Major section breaks
XL:  48px  - Page sections
XXL: 64px  - Major divisions
```

**Vertical Rhythm:**
- Line height: 1.5 for body text, 1.2 for headings
- Consistent spacing between sections
- Use multiples of base spacing unit

### 1.3 Responsive Breakpoints

```css
Mobile:    < 768px   (1 column)
Tablet:    768-1024px (2 columns)
Desktop:   1024-1440px (3 columns)
Wide:      > 1440px  (4 columns)
```

**Responsive Design Checklist:**
- [ ] Layout adapts to screen size
- [ ] Text remains readable (min 16px on mobile)
- [ ] Touch targets ≥ 44x44px on mobile
- [ ] No horizontal scrolling
- [ ] Images scale appropriately
- [ ] Navigation accessible on all devices

---

## 🎨 2. Color System

### 2.1 Color Palette Structure

**Base Colors:**
```
Primary:    Main brand color (CTAs, links, highlights)
Secondary:  Supporting brand color (accents, badges)
Neutral:    Grays for text, backgrounds, borders
Success:    Green (#00873c, #4CAF50)
Warning:    Orange/Yellow (#FFA726, #FFF3CD)
Error:      Red (#d60000, #F44336)
Info:       Blue (#2196F3, #D4EDDA)
```

**Neutral Scale (Gray):**
```
50:  #FAFAFA  - Lightest background
100: #F5F5F5  - Light background
200: #EEEEEE  - Borders
300: #E0E0E0  - Dividers
400: #BDBDBD  - Disabled
500: #9E9E9E  - Placeholder
600: #757575  - Secondary text
700: #616161  - Body text
800: #424242  - Headings
900: #212121  - Darkest text
```

### 2.2 Color Usage Guidelines

**Text Colors:**
- Primary text: Gray 800-900 on light backgrounds
- Secondary text: Gray 600-700
- Disabled text: Gray 400-500
- Links: Primary color (underline on hover)

**Background Colors:**
- Page background: White or Gray 50
- Card background: White
- Hover states: Gray 100
- Selected states: Primary color (10% opacity)

**Semantic Colors:**
- Success: Green backgrounds for positive states
- Warning: Yellow/Orange for caution
- Error: Red for failures
- Info: Blue for informational messages

### 2.3 Color Accessibility

**Contrast Ratios (WCAG 2.1):**
- Normal text: Minimum 4.5:1
- Large text (18px+): Minimum 3:1
- UI components: Minimum 3:1

**Color Blindness Considerations:**
- Don't rely on color alone
- Use icons + text labels
- Test with color blindness simulators
- Provide alternative indicators (patterns, shapes)

---

## 📝 3. Typography

### 3.1 Font Selection

**Font Pairing Strategies:**
- **Monochrome**: Single font family (different weights)
- **Contrast**: Serif headings + Sans-serif body
- **Harmony**: Two fonts from same designer/era

**Recommended Font Stacks:**
```css
/* Modern Sans-Serif */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Classic Serif */
font-family: 'Merriweather', Georgia, 'Times New Roman', serif;

/* Monospace (code) */
font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
```

### 3.2 Type Scale

**Modular Scale (1.250 - Major Third):**
```
H1: 39px  (2.441rem) - Page titles
H2: 31px  (1.953rem) - Section headings
H3: 25px  (1.563rem) - Subsection headings
H4: 20px  (1.250rem) - Card titles
H5: 16px  (1.000rem) - Small headings
Body: 16px (1.000rem) - Base text
Small: 13px (0.800rem) - Captions, labels
Tiny: 10px (0.640rem) - Metadata
```

### 3.3 Typography Best Practices

**Readability:**
- Line length: 50-75 characters (optimal 66)
- Line height: 1.5 for body, 1.2 for headings
- Paragraph spacing: 1em between paragraphs
- Letter spacing: Default for body, slight increase for uppercase

**Hierarchy:**
- Use size, weight, and color to create hierarchy
- Limit to 3-4 font sizes per page
- Consistent heading styles across pages
- Clear distinction between headings and body

**Font Weights:**
```
Light:    300 - Decorative headings
Regular:  400 - Body text
Medium:   500 - Emphasis
Semibold: 600 - Subheadings
Bold:     700 - Headings, CTAs
```

---

## 🔘 4. Interactive Elements

### 4.1 Buttons

**Button Hierarchy:**
```
Primary:   Filled, high contrast (main action)
Secondary: Outlined, medium contrast (alternative action)
Tertiary:  Text only, low contrast (minor action)
Danger:    Red, for destructive actions
```

**Button Sizes:**
```
Small:  padding: 6px 12px, font: 13px
Medium: padding: 10px 20px, font: 16px
Large:  padding: 14px 28px, font: 18px
```

**Button States:**
- Default: Base color
- Hover: Slightly darker (10-20%)
- Active: Pressed appearance (inset shadow)
- Disabled: Gray, reduced opacity (0.5-0.6)
- Loading: Spinner + disabled state

**Best Practices:**
- [ ] Clear, action-oriented labels ("Save", not "OK")
- [ ] Consistent placement (primary on right)
- [ ] Adequate spacing between buttons (8-16px)
- [ ] Icon + text for clarity (optional)
- [ ] Minimum touch target: 44x44px

### 4.2 Form Elements

**Input Fields:**
```
Height: 40-48px
Padding: 10-12px
Border: 1px solid Gray 300
Border-radius: 4-8px
Focus: Primary color border + shadow
Error: Red border + error message below
```

**Input States:**
- Default: Gray border
- Focus: Primary color border, subtle shadow
- Filled: Darker text, normal border
- Error: Red border, red text, error icon
- Disabled: Gray background, gray text
- Read-only: No border, gray background

**Form Layout:**
- [ ] Labels above inputs (mobile-friendly)
- [ ] Required fields marked with asterisk
- [ ] Helpful placeholder text
- [ ] Inline validation (real-time feedback)
- [ ] Error messages below fields
- [ ] Group related fields together

### 4.3 Toggles & Checkboxes

**Toggle Switch:**
- Use for on/off states
- Show current state clearly
- Immediate effect (no save button)
- Label describes what's being toggled

**Checkbox:**
- Use for multiple selections
- Clear checked/unchecked states
- Label to the right of checkbox
- Group related checkboxes

**Radio Buttons:**
- Use for single selection from list
- Show all options at once
- One option pre-selected (if applicable)
- Clear visual grouping

### 4.4 Dropdowns & Selects

**Dropdown Menu:**
```
Trigger: Button or text with down arrow
Menu: White background, subtle shadow
Items: Hover state, active state
Max height: 300px (scrollable)
```

**Best Practices:**
- [ ] Searchable for 7+ items
- [ ] Keyboard navigation support
- [ ] Clear selected state
- [ ] Placeholder text when empty
- [ ] Group related options

---

## 📊 5. Data Visualization

### 5.1 Chart Design Principles

**Clarity:**
- Clear axis labels and units
- Readable legends
- Appropriate chart type for data
- Minimal chart junk (no 3D, gradients)

**Color Usage:**
- Consistent color meanings
- Colorblind-friendly palettes
- Highlight important data
- Use neutral colors for context

**Recommended Chart Types:**
- **Line**: Trends over time
- **Bar**: Comparisons across categories
- **Pie**: Parts of a whole (use sparingly)
- **Scatter**: Correlations
- **Heatmap**: Patterns in matrix data

### 5.2 Table Design

**Table Structure:**
```
Header: Bold, background color, sticky on scroll
Rows: Alternating backgrounds (zebra striping)
Cells: Padding 12px, left-aligned text, right-aligned numbers
Borders: Subtle horizontal lines
```

**Table Features:**
- [ ] Sortable columns (click header)
- [ ] Filterable data
- [ ] Pagination for large datasets
- [ ] Row hover state
- [ ] Responsive (stack on mobile)
- [ ] Fixed header on scroll

**Data Formatting:**
- Numbers: Right-aligned, consistent decimals
- Dates: Consistent format (YYYY-MM-DD)
- Currency: Symbol + formatted number
- Percentages: % symbol, 1-2 decimals
- Long text: Truncate with ellipsis + tooltip

### 5.3 Cards & Containers

**Card Design:**
```
Background: White
Border: 1px solid Gray 200 or subtle shadow
Border-radius: 8-12px
Padding: 16-24px
Spacing: 16-24px between cards
```

**Card Anatomy:**
- Header: Title + optional actions
- Body: Main content
- Footer: Metadata or actions (optional)

**Card Variations:**
- Flat: No shadow, border only
- Elevated: Subtle shadow
- Outlined: Border, no shadow
- Interactive: Hover effect, clickable

---

## 🎭 6. Visual Feedback & States

### 6.1 Loading States

**Indicators:**
- Spinner: Indeterminate progress
- Progress bar: Determinate progress (%)
- Skeleton screens: Content placeholders
- Pulse animation: Loading shimmer

**Best Practices:**
- [ ] Show loading immediately (< 100ms)
- [ ] Provide context ("Loading data...")
- [ ] Disable actions during loading
- [ ] Timeout after reasonable period
- [ ] Error state if loading fails

### 6.2 Empty States

**Components:**
- Icon or illustration
- Heading: "No data yet"
- Description: Why it's empty
- Action: How to add data (if applicable)

**Examples:**
```
No tickers added yet
Add your first ticker to get started
[Add Ticker] button
```

### 6.3 Error States

**Error Message Structure:**
- What happened: "Failed to load data"
- Why: "Network connection lost"
- What to do: "Check connection and try again"
- Action: [Retry] button

**Error Severity:**
- Info: Blue, informational
- Warning: Orange, caution
- Error: Red, failure
- Success: Green, confirmation

### 6.4 Success Feedback

**Toast Notifications:**
```
Position: Top-right or bottom-center
Duration: 3-5 seconds
Dismissible: X button
Icon: Checkmark for success
```

**Inline Feedback:**
- Green checkmark next to saved field
- Success banner at top of page
- Confirmation modal for critical actions

---

## 🎯 7. Navigation & Information Architecture

### 7.1 Navigation Patterns

**Top Navigation:**
- Logo/brand (left)
- Main menu items (center/left)
- User actions (right)
- Sticky on scroll (optional)

**Sidebar Navigation:**
- Collapsible sections
- Active state highlighting
- Icons + text labels
- Scrollable if many items

**Tab Navigation:**
- Horizontal tabs for related content
- Active tab clearly indicated
- Underline or background highlight
- Keyboard navigation support

**Breadcrumbs:**
- Show current location
- Clickable parent pages
- Separator: / or >
- Don't show on top-level pages

### 7.2 Information Hierarchy

**Priority Levels:**
1. **Primary**: Main content, key actions
2. **Secondary**: Supporting content, alternative actions
3. **Tertiary**: Metadata, minor actions

**Visual Hierarchy Techniques:**
- Size: Larger = more important
- Color: High contrast = more important
- Position: Top/left = more important
- Spacing: More whitespace = more important
- Weight: Bold = more important

### 7.3 Search & Filters

**Search Box:**
- Prominent placement
- Clear placeholder text
- Search icon (left or right)
- Clear button when text entered
- Real-time results (if applicable)

**Filters:**
- Group related filters
- Show active filter count
- Clear all filters option
- Preserve filters across navigation
- Mobile: Collapsible filter panel

---

## 📱 8. Mobile-First Design

### 8.1 Mobile Considerations

**Touch Targets:**
- Minimum: 44x44px
- Spacing: 8px between targets
- Larger for primary actions

**Navigation:**
- Hamburger menu for complex navigation
- Bottom navigation for 3-5 main items
- Sticky header with key actions
- Swipe gestures for natural interactions

**Content:**
- Single column layout
- Larger text (16px minimum)
- Simplified forms (fewer fields)
- Progressive disclosure (show more)

### 8.2 Mobile Patterns

**Collapsible Sections:**
- Accordion for long content
- Expandable cards
- "Show more" buttons
- Drawer panels from bottom/side

**Mobile Tables:**
- Stack columns vertically
- Show key columns only
- Horizontal scroll for full table
- Card view for complex data

---

## 🎨 9. Design Patterns Library

### 9.1 Common Patterns

**Dashboard Metrics:**
```
┌─────────────────┐
│ 📊 Metric Name  │
│                 │
│    1,234        │ Large number
│    +5.2%        │ Change indicator
└─────────────────┘
```

**News Feed:**
```
🟢 10:30 AM - Breaking: Market update...
🟡 Yesterday - Analysis: Tech sector trends...
⚪ 2 days ago - Report: Economic indicators...
```

**Time-Based Color Coding:**
- Dark Green: < 10 minutes
- Light Green: < 1 hour
- Yellow: Yesterday
- Gray: Older

**Status Indicators:**
- ✅ Success / Complete
- ⚠️ Warning / Pending
- ❌ Error / Failed
- ⏳ In Progress
- ⭕ Empty / Not Started

### 9.2 Micro-interactions

**Hover Effects:**
- Subtle color change (10-20% darker)
- Scale slightly (1.02-1.05x)
- Shadow increase
- Underline for links

**Click/Tap Feedback:**
- Button press animation
- Ripple effect
- Color change
- Haptic feedback (mobile)

**Transitions:**
- Duration: 150-300ms
- Easing: ease-in-out
- Fade: Opacity changes
- Slide: Position changes
- Scale: Size changes

---

## ♿ 10. Accessibility (A11y)

### 10.1 WCAG 2.1 Guidelines

**Level A (Minimum):**
- [ ] Text alternatives for images
- [ ] Keyboard accessible
- [ ] Color not sole indicator
- [ ] Clear focus indicators

**Level AA (Recommended):**
- [ ] 4.5:1 contrast for text
- [ ] 3:1 contrast for UI components
- [ ] Resizable text (200%)
- [ ] Multiple ways to navigate

**Level AAA (Enhanced):**
- [ ] 7:1 contrast for text
- [ ] No time limits
- [ ] Descriptive headings
- [ ] Consistent navigation

### 10.2 Semantic HTML

**Use Proper Elements:**
```html
<header> - Page/section header
<nav> - Navigation
<main> - Main content
<article> - Self-contained content
<section> - Thematic grouping
<aside> - Sidebar content
<footer> - Page/section footer
<button> - Interactive button
<a> - Links to other pages
```

### 10.3 ARIA Labels

**When to Use:**
- Icon-only buttons: `aria-label="Close"`
- Dynamic content: `aria-live="polite"`
- Hidden content: `aria-hidden="true"`
- Expanded state: `aria-expanded="true"`
- Current page: `aria-current="page"`

---

## 🎨 11. Streamlit-Specific Design

### 11.1 Streamlit Layout

**Columns:**
```python
col1, col2, col3 = st.columns([1, 2, 1])  # Ratio-based
col1, col2 = st.columns(2)  # Equal width
```

**Containers:**
```python
with st.container():  # Grouping
with st.expander("Details"):  # Collapsible
with st.sidebar:  # Sidebar content
```

**Tabs:**
```python
tab1, tab2, tab3 = st.tabs(["📊 Charts", "📰 News", "⚙️ Settings"])
```

### 11.2 Streamlit Custom CSS

**Inject Custom Styles:**
```python
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    .metric-card {
        padding: 20px;
        border-radius: 8px;
        background: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)
```

**Common Customizations:**
- Remove padding: `.block-container { padding-top: 1rem; }`
- Hide menu: `#MainMenu { visibility: hidden; }`
- Custom fonts: `@import url('https://fonts.googleapis.com/...')`
- Image sizing: `[data-testid="stImage"] img { height: 350px; }`

### 11.3 Streamlit Best Practices

**Performance:**
- Use `@st.cache_data` for expensive operations
- Lazy load images
- Paginate large datasets
- Debounce user inputs

**UX:**
- Show loading spinners: `with st.spinner("Loading...")`
- Toast notifications: `st.toast("Saved!")`
- Success/error messages: `st.success()`, `st.error()`
- Progress bars: `st.progress(0.5)`

---

## 📋 12. Design Checklist

### Pre-Design
- [ ] Define user personas
- [ ] List core user journeys
- [ ] Identify key features
- [ ] Establish design goals
- [ ] Review competitor designs

### Design Phase
- [ ] Create color palette
- [ ] Define typography scale
- [ ] Design component library
- [ ] Create layout templates
- [ ] Design key screens/pages

### Implementation
- [ ] Set up design system
- [ ] Implement responsive layouts
- [ ] Add interactive states
- [ ] Test accessibility
- [ ] Optimize performance

### Post-Launch
- [ ] Gather user feedback
- [ ] A/B test variations
- [ ] Monitor analytics
- [ ] Iterate on design
- [ ] Document patterns

---

## 🎯 Quick Reference

### Design Principles
1. **Clarity** - Make it obvious
2. **Consistency** - Use patterns
3. **Feedback** - Respond to actions
4. **Efficiency** - Minimize effort
5. **Forgiveness** - Allow undo
6. **Delight** - Add personality

### Common Mistakes to Avoid
- ❌ Too many colors (stick to 2-3)
- ❌ Inconsistent spacing
- ❌ Poor contrast (unreadable text)
- ❌ Too many font sizes
- ❌ Unclear CTAs
- ❌ No loading states
- ❌ Ignoring mobile users
- ❌ No error handling

### Resources
- **Colors**: Coolors.co, Adobe Color
- **Fonts**: Google Fonts, Font Pair
- **Icons**: Heroicons, Feather Icons, Font Awesome
- **Inspiration**: Dribbble, Behance, Awwwards
- **Accessibility**: WebAIM, A11y Project
- **Tools**: Figma, Sketch, Adobe XD

---

**Last Updated:** January 13, 2026  
**Version:** 1.0  
**Framework Type:** UI/UX Design Guidelines
