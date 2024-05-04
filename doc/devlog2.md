# Usability

## Removal of E2EE Chat

The end-to-end encrypted chat feature is removed to enhance usability. This feature is complex and requires a deep understanding of cryptography. The main problem lies in progressing to multi-user chat rooms, which necessitates a more intricate encryption scheme. As this is beyond the scope of this project, we opt to remove the chat encryption feature entirely.

Here's a proposed multi-user chat encryption scheme: When a chatroom is created, the first user of the room would create a symmetric key and encrypt it with the public keys of all other users in the room. The encrypted key would then be sent to the server, which would distribute it to the other users. This way, all users in the chatroom would have the symmetric key to encrypt and decrypt messages. When another user joins the chatroom, the symmetric key would be re-encrypted with the new user's public key and sent to the server for redistribution.

## Separated File Structure

For larger projects, it is crucial to separate and organize different components of the code. We divide the CSS, JavaScript, and Jinja (HTML) into distinct files. This restructuring of the framework also supports Content Security Policy (CSP), which effectively helps prevent XSS attacks.

To eliminate all inline JavaScript, we must alter the logic associated with input fields and buttons. This involves using selectors to identify these elements and attaching functions to their events within a JavaScript file.

## Bootstrap 5

Bootstrap 5 is a CSS framework that offers a variety of visually appealing designs. Its usage mirrors that of employing a user-defined CSS file: include the framework file and assign classes to the elements. However, mastering it still requires some learning. For instance, Bootstrap’s grid system differs from traditional grids, necessitating an understanding of the box model. Users also need to know which classes to apply to achieve the desired effects.

## Online status

To update the online status of users in time, we utilize WebSockets' connect event. The server would maintain a dict mapping all users to their WebSocket connections. When a user's connection status changes, the server would emit a message to all of the user's friends, updating their online status. The users would also receive their friends' online status when they log in.

In order to provide a better visual experience, we uses dedicated css and js.