# Dev Log

![task](task.jpg)

Certain libraries required by the project lack support in Python 3.12. The project was developed using Python 3.11.8.

## Design Overview

### Friends

The key design of the friends feature is the utilization of SQLAlchemy's ORM framework. We crafted tables for friendships and pending friend requests, employing a many-to-many self-referential relationship schema. This approach streamlines querying and managing friendships. However, given the intricacies of SQLAlchemy 2's syntax, we opted for a unidirectional design for the friendship table.

Further enhancements include:

1. Integration of a user interface to showcase friends and pending friend requests, leveraging Flask's Jinja2 templating engine.
2. Creation of an input field and JavaScript functionality to initiate friend requests.
3. Implementation of buttons and JavaScript for accepting or declining friend requests.
4. Development of backend routes and database operations to process friend requests.
5. Incorporation of validation checks during the process of adding friends to the database.
6. Addition of JavaScript enabling users to initiate chats by clicking on a friend's name.
