import React from 'react';

function MainInterface() {
  return (
    <div className="w-full h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">Voxie AI - Main Interface</h1>
        <p className="text-gray-600">Welcome to the main interface. Your AI assistant is ready to help!</p>
      </div>
    </div>
  );
}

export default MainInterface;
