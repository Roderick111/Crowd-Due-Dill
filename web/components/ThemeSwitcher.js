/**
 * ThemeSwitcher.js - Theme Switch Button Component
 * Purpose: Provides a button to toggle between light and dark themes
 */

const ThemeSwitcher = () => {
    const { theme, setTheme, mounted } = useTheme();

    // Don't render until mounted to avoid hydration mismatch
    if (!mounted) {
        return React.createElement('div', { 
            className: "w-10 h-10 flex items-center justify-center" 
        });
    }

    const toggleTheme = () => {
        setTheme(theme === 'dark' ? 'light' : 'dark');
    };

    return React.createElement('button', {
        onClick: toggleTheme,
        className: "w-10 h-10 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center justify-center transition-colors",
        title: `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`
    }, 
        // Half-circle icon representing light/dark toggle
        React.createElement('svg', {
            className: "w-5 h-5",
            fill: "currentColor",
            viewBox: "0 0 24 24"
        }, 
            React.createElement('circle', {
                cx: "12",
                cy: "12", 
                r: "10",
                fill: "none",
                stroke: "currentColor",
                strokeWidth: "2"
            }),
            React.createElement('path', {
                d: "M12 2a10 10 0 0 0 0 20z",
                fill: "currentColor"
            })
        )
    );
};

// Export for global use
window.ThemeSwitcher = ThemeSwitcher; 