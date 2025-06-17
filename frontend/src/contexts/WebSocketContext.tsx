import React, { createContext, useContext, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';

interface WebSocketContextType {
    sendMessage: (message: string) => void;
    lastMessage: string | null;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const ws = useRef<WebSocket | null>(null);
    const clientId = useRef(uuidv4());
    const [lastMessage, setLastMessage] = React.useState<string | null>(null);

    useEffect(() => {
        ws.current = new WebSocket(`ws://localhost:8000/ws/${clientId.current}`);

        ws.current.onmessage = (event) => {
            setLastMessage(event.data);
        };

        ws.current.onclose = () => {
            console.log('WebSocket connection closed');
        };

        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, []);

    const sendMessage = (message: string) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(message);
        }
    };

    return (
        <WebSocketContext.Provider value={{ sendMessage, lastMessage }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => {
    const context = useContext(WebSocketContext);
    if (context === undefined) {
        throw new Error('useWebSocket must be used within a WebSocketProvider');
    }
    return context;
}; 