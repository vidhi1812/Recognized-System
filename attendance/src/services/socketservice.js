import { io } from 'socket.io-client';

const socket = io('http://localhost:4001'); // Update with backend URL

export const listenForAttendanceUpdates = (callback) => {
    socket.on('attendanceUpdated', callback);
};
