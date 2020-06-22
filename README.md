# Django Polls API

​	A simple 3 model base polling system that allows to create distinct polls, and generate a result of those polls by age and gender of the participants. It also allows the chance tao create quantitative questions  that are evaluated through Natural Lenguage Procesing, to create a world cloud. 

## Technologies

​	The core response processioning,  works with a simple statistics to generate response distribution, it can process two kind of responses, Open Text, and 1-5 hierarchy, Every poll can have many questions, and the questions can extract its responses from different polls, in the case of open text responses the system  uses the  NLTK toolkit (optimized for Spanish) to generate a count of the words responded, distributing it by age or gender. 

​	The app is based on Django Rest Framework, and depends on a relational database to work, the basic polls application uses a reference to the base user an to a extended "Profiles model" to generate the statistics.