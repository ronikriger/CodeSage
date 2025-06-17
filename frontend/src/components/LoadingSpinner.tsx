import React from 'react';

interface LoadingSpinnerProps {
    size?: 'small' | 'medium' | 'large';
    color?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
    size = 'medium',
    color = 'blue-600'
}) => {
    const sizeClasses = {
        small: 'w-4 h-4',
        medium: 'w-8 h-8',
        large: 'w-12 h-12'
    };

    return (
        <div className="flex justify-center items-center">
            <div className={`${sizeClasses[size]} border-4 border-gray-200 border-t-${color} rounded-full animate-spin`} />
        </div>
    );
};

export default LoadingSpinner; 