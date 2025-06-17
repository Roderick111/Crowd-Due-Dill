/**
 * app.js - Main Application Layout & Component Orchestration
 * Purpose: Pure presentation layer that composes UI components and distributes props.
 * Contains NO business logic - delegates all functionality to useAppLogic hook.
 */

const { useState, useEffect, useRef } = React;

// Main Chat Application Component
function App() {
    // Use our custom hook for all business logic
    const {
        // State
        messages,
        inputValue,
        setInputValue,
        isLoading,
        systemStatus,
        sessions,
        currentSessionId,
        sidebarOpen,
        setSidebarOpen,
        showSettingsModal,
        setShowSettingsModal,

        showProfileMenu,
        setShowProfileMenu,
        showArchivedModal,
        setShowArchivedModal,
        suggestionsDismissed,
        selectedSuggestion,
        isNewSession,
        showSuggestions,
        
        // Refs
        messagesEndRef,
        inputRef,
        
        // Functions
        handleSuggestionClick,
        dismissSuggestions,
        openSettingsModal,

        openArchivedModal,
        sendMessage,

        createNewSession,
        loadSessionMessages,
        updateSessionTitle,
        archiveSession,
        deleteSession,
        handleMessageAction
    } = useAppLogic();

    return (
        <ThemeProvider>
            <div className="flex flex-col h-screen text-white bg-gray-900 overflow-hidden">
                <div className="flex flex-1 min-h-0">
                {/* Left Sidebar */}
            <Sidebar 
                sidebarOpen={sidebarOpen}
                setSidebarOpen={setSidebarOpen}
                systemStatus={systemStatus}
                sessions={sessions}
                currentSessionId={currentSessionId}
                onCreateNewSession={createNewSession}
                onLoadSession={loadSessionMessages}
                onUpdateSessionTitle={updateSessionTitle}
                onArchiveSession={archiveSession}
                onDeleteSession={deleteSession}
            />

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col relative min-h-0">
                {/* Top Bar - Overlay */}
                <div className="absolute top-0 left-0 right-0 z-50 pointer-events-none">
                    <div className="pointer-events-auto">
                        <TopBar 
                            sidebarOpen={sidebarOpen}
                            setSidebarOpen={setSidebarOpen}
                            currentSessionId={currentSessionId}
                            sessions={sessions}
                            showProfileMenu={showProfileMenu}
                            setShowProfileMenu={setShowProfileMenu}
                            onOpenSettingsModal={openSettingsModal}

                            onOpenArchivedModal={openArchivedModal}
                            systemStatus={systemStatus}

                        />
                    </div>
                </div>

                {/* Chat Area - Fixed Height Container */}
                <div className="flex-1 flex flex-col min-h-0">
                <ChatArea 
                    messages={messages}
                    isLoading={isLoading}
                    inputValue={inputValue}
                    setInputValue={setInputValue}
                    onSendMessage={sendMessage}
                    messagesEndRef={messagesEndRef}
                    inputRef={inputRef}
                    systemStatus={systemStatus}
                    isNewSession={isNewSession}
                    suggestionsDismissed={suggestionsDismissed}
                    selectedSuggestion={selectedSuggestion}
                    onSuggestionClick={handleSuggestionClick}
                    onDismissSuggestions={dismissSuggestions}
                    onMessageAction={handleMessageAction}
                />
            </div>
            </div>
            </div>

                        {/* Modals */}
            <Modals
                showSettingsModal={showSettingsModal}
                setShowSettingsModal={setShowSettingsModal}

                showProfileMenu={showProfileMenu}
                setShowProfileMenu={setShowProfileMenu}
                systemStatus={systemStatus}

            />

            {/* Archived Sessions Modal */}
            <ArchivedSessions
                showArchivedModal={showArchivedModal}
                setShowArchivedModal={setShowArchivedModal}
                onLoadSession={loadSessionMessages}
                onDeleteSession={deleteSession}
            />


        </div>
        </ThemeProvider>
    );
}

// Render the app
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />); 