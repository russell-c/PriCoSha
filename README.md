# PriCoSha
Flask and PyMySQL application that allows users to share and view content sent to friend groups

# Project Description

This is PriCoSha. A system in which users can share content items with the public or their specific friend groups. Users can tag their friends in posts, accept tag requests and rate or comment on posts that have been shared to them. Not on good terms with an old friend? No worries! You can even defriend a person from your friend group and totally shut them out. Security is not an issue with PriCoSha because all passwords are encrypted with SHA-2 hash encryption so you and only you will have access to your information.

# Additional Features Implemented

- Commenting : 
  - Implemented by Russell Coke
  - In addition to rating an image, users can leave full blown text-based comments to a post that has been shared with them. The comment is inserted into the "comment" table in the database along with the timestamp, the email address of the commenter and the item_id. The textfield to add a comment, as well as the list of existing comments on a content item, can be found on the page that also displays the ratings of the item and the tagged users in the item.
  - This is a good feature to have beacause it allows users the opportunity to express themselves more. Apps like Instagram and Facebook all allow users to react to and comment on a post by their friend, so we wanted to do the same.
  - A new table called "comment" was added. It has the attributes:
    - email: the email of the commenter
    - item_id: the id of the item being commented on
    - comment_time: the timestamp the commented was submitted
    - comment: the text of the comment
  - Here is how it looks in the application
  ![comments-screen](misc/comments-screen.png?raw=true "Comments Webpage")
  - Here is the view of the database
  ![comments-screen](misc/comments-db.png?raw=true "Comments Webpage")

- Defriending:
  - Implemented by Robert Gordon
  - If you and another user are no longer friends, you can remove that user from all your friends groups on the app. In addition to removing them from your groups, it also removes any tags of that person from the "tag" table for all the content items posted in the groups that you own. If the removed user tagged someone else that tag remains, however, because the other  person shouldn't be affected by this defriending process.
  - This is a good feature to have because people's friend groups in real life are always changing and we wanted our application to reflect that dynamic. This is also about privacy. No one should have access to your content if you disapprove.
  - No new tables were introduced for this feature
  - Here is how it looks in the application
  ![comments-screen](misc/defriend-screen.png?raw=true "Defriend Webpage"
  - Here is the before picture of the database
  ![comments-screen](misc/defriend-db-before.png?raw=true "Defriend DB Before"
  - Here is the before picture of the database
  ![comments-screen](misc/defriend-db-after.png?raw=true "Defriend DB After"
  
# Contributions
Russell Coke: Styling, Database Design and Modelling, Feature Development and Implementation, Testing
- Implemented:
  - Login
  - Viewing shared content
  - Tagging
  - Displaying rates and commenting
  - Manage tag requests
  
Robert Gordon: Database Design and Modelling, Feature Development and Implementation, Testing
- Implemented:
  - Adding friends
  - Sharing content
  - Removing friends
  - Viewing public content
