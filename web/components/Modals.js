/**
 * Modals.js - Modal Management System
 * Purpose: Handles Settings modal with backdrop click-to-close functionality.
 * Centralizes all overlay UI components and their interaction logic.
 */
const Modals = ({
    showSettingsModal,
    setShowSettingsModal,
    showProfileMenu,
    setShowProfileMenu,
    systemStatus
}) => {
    return (
        <>
            {/* Settings Modal */}
            {showSettingsModal && (
                <div 
                    className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                    onClick={() => setShowSettingsModal(false)}
                >
                    <div 
                        className="bg-gray-800 rounded-lg w-full max-w-2xl max-h-[80vh] overflow-y-auto"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="p-6 border-b border-gray-700 flex items-center justify-between">
                            <h2 className="text-xl font-semibold">Settings</h2>
                            <button
                                onClick={() => setShowSettingsModal(false)}
                                className="p-2 hover:bg-gray-700 rounded"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        
                        <div className="p-6">
                            {/* System Information */}
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold mb-4">System Information</h3>
                                <div className="space-y-3">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <div className="font-medium">Knowledge Domain</div>
                                            <div className="text-sm text-gray-400">
                                                EU Crowdfunding Regulations (EU) 2020/1503
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                            <span className="text-green-400 text-sm">Active</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Click outside to close profile menu */}
            {showProfileMenu && (
                <div 
                    className="fixed inset-0 z-40" 
                    onClick={() => {
                        setShowProfileMenu(false);
                    }}
                ></div>
            )}
        </>
    );
};

// Export for use in other components
window.Modals = Modals; 