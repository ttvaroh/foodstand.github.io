# FoodStand
## Video Demo: [https://youtu.be/YKNCfbeUlY4](https://youtu.be/YKNCfbeUlY4)
## Description:
    Foodstand is a website that allows users to store data and instructions about their favorite recipes. It allows users to store ingredients, descriptions, type of meal, and more. Once a recipe has been added to the database, it is displayed on the user's homepage for easy access and reference.


### Inspiration
    I developed Foodstand because my dad and I love to cook together. However, we often struggled with remembering or finding our old recipes. I saw this as an opportunity to combine my passion for cooking with my knowledge from the CS50 course and create a solution to this problem. Now, with Foodstand, we are able to store all of our recipes on a reliable database and easily access them whenever we want to cook something new.

### Design Choice
    While the majority of my efforts went into fixing bugs in the code, I also made several important design choices. One such choice was to prevent user exploitation by limiting the number of ingredients that can be added to a recipe at any given moment. Previously, users could add an unlimited number of ingredients, which could have caused issues with the database. To solve this, I implemented JavaScript that requires users to fill out all previous ingredient forms and their respective ingredient amounts before adding a new one. This helps to ensure that the database remains organized and efficient.

    Another design choice I made was to address an issue that arose when users deleted ingredients from their recipe. I noticed that this caused issues with "for loops" in the code because of the way I had named each ingredient. To fix this, I used JavaScript to rename each ingredient and amount after one had been deleted. This helps to keep the database organized and prevents errors in the code.


### Conclusion
    Overall, Foodstand is a user-friendly and efficient tool for storing and organizing recipes. It allows users to easily access and reference their favorite recipes, while also providing features to prevent user exploitation and maintain a organized database.