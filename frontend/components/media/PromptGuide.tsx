
import React from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";

const features = [
    {
        category: "Basic Edits",
        color: "blue",
        items: [
            {
                title: "Trim Video",
                description: "Cut a video to a specific start and end time.",
                example: "Trim the video from 0:10 to 0:30."
            },
            {
                title: "Concatenate Videos",
                description: "Combine multiple video clips into one.",
                example: "Combine video A and video B."
            },
            {
                title: "Change Speed",
                description: "Speed up or slow down a video.",
                example: "Make the video 2x faster."
            }
        ]
    },
    {
        category: "Audio Edits",
        color: "purple",
        items: [
            {
                title: "Extract Audio",
                description: "Separate the audio from a video clip.",
                example: "Extract the audio from this video."
            },
            {
                title: "Add Audio",
                description: "Add a new audio track to a video.",
                example: "Add this music to the video."
            },
            {
                title: "Combo: Extract & Add",
                description: "Extract audio from one video and add it to another.",
                example: "Take the audio from video A and add it to video B."
            }
        ]
    },
    {
        category: "Visual Effects",
        color: "green",
        items: [
            {
                title: "Add Text",
                description: "Overlay text on a video.",
                example: "Add the text 'Hello World' at the beginning."
            },
            {
                title: "Apply Filters",
                description: "Add visual filters like grayscale, sepia, etc.",
                example: "Apply a black and white filter."
            },
            {
                title: "Add Transitions",
                description: "Add fade-in or fade-out effects.",
                example: "Add a fade-in at the start and fade-out at the end."
            }
        ]
    },
    {
        category: "Advanced Edits",
        color: "yellow",
        items: [
            {
                title: "Sequential Edits",
                description: "Chain multiple commands together.",
                example: "Trim the video to 10 seconds, then make it black and white."
            },
            {
                title: "Multi-File Edits",
                description: "Apply edits to multiple files at once.",
                example: "Trim the first 5 seconds of every video, then combine them."
            }
        ]
    }
];

const PromptGuide = () => {
    return (
        <div className="bg-gray-800 rounded-lg p-4 h-full overflow-y-auto flex flex-col">
            <div className="flex items-center justify-center gap-3 mb-4 flex-shrink-0">
                <h2 className="text-3xl font-lobster text-center py-2 flex-shrink-0 text-white">Prompt Guide</h2>
            </div>

            <div className="space-y-6 overflow-y-auto">
                {features.map((feature, idx) => (
                    <div key={idx}>
                        <h3 className="text-sm font-semibold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-3">{feature.category}</h3>
                        <div className="space-y-3">
                            {feature.items.map((item, itemIdx) => (
                                <div key={itemIdx} className="bg-gray-900/50 p-3 rounded-md border border-gray-700/50">
                                    <p className="font-medium text-white text-sm">{item.title}</p>
                                    <p className="text-xs text-gray-400 mt-1">{item.description}</p>
                                    <p className="text-xs text-gray-500 mt-2 italic">e.g., "{item.example}"</p>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PromptGuide;
