'use client';

import { useState, useRef } from 'react';
import { useAppStore } from '@/store/appStore';

// --- REFACTORED to be a reusable component ---
const FileUploader = ({
    accept,
    title,
    onFileUpload
}: {
    accept: string;
    title: string;
    onFileUpload: (file: File) => Promise<void>;
}) => {
    const [isDragging, setIsDragging] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const { isUploading, uploadProgress } = useAppStore(); // Get global upload state

    const handleFileValidation = (file: File): boolean => {
        const fileType = file.type;
        const acceptedTypes = accept.split(',').map(t => t.trim());
        const isValid = acceptedTypes.some(t => {
            if (t.endsWith('/*')) {
                return fileType.startsWith(t.slice(0, -1));
            }
            return fileType === t;
        });

        if (!isValid) {
            setError(`Invalid file type. Please upload a ${title.toLowerCase()}.`);
            return false;
        }
        setError(null);
        return true;
    };

    const handleUpload = async (file: File) => {
        if (!handleFileValidation(file)) return;
        await onFileUpload(file);
    };

    // ... (drag/drop and click handlers remain the same, but use the new validation)

    return (
        <div className="space-y-3">
            <div
                // ... (drag/drop handlers)
                onClick={() => fileInputRef.current?.click()}
                className={`...`}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept={accept} // <-- Use prop
                    onChange={handleFileSelect}
                    className="hidden"
                />

                {isUploading ? (
                    // ... (progress bar)
                ): (
                        <div>
            <p className = "text-gray-300 text-lg mb-2">{ title }</p> {/* <-- Use prop */}
            <p className="text-sm text-gray-500">or click to browse</p>
        </div>
    )
}
      </div >
    { error && ( /* ... error display ... */ )}
    </div >
  );
};

export default FileUploader;
