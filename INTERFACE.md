# API Endpoints

[Template](https://gist.github.com/iros/3426278)


**Basic Functionality**

+ Create an issue *(POST)*
+ Create a user *(POST)*
    + NOTE: not secure using http
+ Authenticate a user *(POST)*
    + NOTE: not secure using http
+ Retrieve a node *(GET)*
+ Retrieve all nodes of a given type *(GET)*
+ Rank a node as a user *(POST)*
+ Map a connection between two nodes *(POST)*
+ Generate summary for stacked bar chart visualization *(GET)*



**Create an Issue**
----
  Send issue information and Value|Objective|Policy node information
  to create an issue

* **Method:**
  
  `POST`

* **URL**

  + `/api/issue`

* **Data Params**

  ```
  {
    issue_name:     <name string>,          // required
    desc:           <description string>,   // optional
    values:         [ <name string>, ... , <name string> ],
    objectives:     [ <name string>, ... , <name string> ],
    policies:       [ <name string>, ... , <name string> ]
  }
  ```
  
* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:**
    
    ```
    {
      success:      [boolean],
      issue_id:     [string]    // issue_id for the newly created issue
    }
    ```

* **Error Response:**

  * **Code:** 422 UNPROCESSABLE ENTITY <br />
    **Cause:** Invalid request parameters


**Create User**
----
  Create a new user (NOTE: not secure unless over https)

* **Method:**
  
  `POST`

* **URL**

  + `/api/user`

* **Data Params**

  ```
  {
    username:   [string],   // must be unique
    password:   [string],
    name:       [string],   // display name
    city:       [string]
  }
  ```
  
* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:**

    ```
    {
      success:  [boolean],
      error:    [string]     // present if success == False
    }
    ```
 
* **Error Response:**

  * **Code:** 422 UNPROCESSABLE ENTITY <br />
    **Cause:** Invalid request parameters


**Authenticate User**
----
  Send username/password credentials to authenticate a user.

* **Method:**
  
  `POST`

* **URL**

  + `/api/login`

* **Data Params**

  ```
  {
    username:    [string],
    password:    [string]
  }
  ```
  
* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:**
    
    ```
    {
      success:  [boolean],  // True or False depending on if user is authenticated
      error:    [string]    // present if success == False
    }
    ```

* **Error Response:**

  * **Code:** 422 UNPROCESSABLE ENTITY <br />
    **Cause:** Invalid request parameters


**Retrieve a Node**
----
  Retrieve data for a specific node.

* **Method:**
  
  `GET`
  
* **URL**

  + `/api/user?id=string`
  + `/api/issue?id=string`
  + `/api/community?id=string`
  + `/api/value?id=string`
  + `/api/objective?id=string`
  + `/api/policy?id=string`
  
*  **URL Params**

   **Required:**
 
   `id=[string]`

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** `{ keys : values }`
 
* **Error Response:**

  * **Code:** 422 UNPROCESSABLE ENTITY <br />
    **Cause:** Invalid request parameters


**Retrieve All Data for a specific entity type**
----
  Retrieve all entities of a specific type for `Communities|Issues|Values|Objectives|Policies`.
  
* **Method:**
  
  `GET`  
  
* **URL**

  + `/api/communnity`
  + `/api/community/issue?filter_id=string` `filter_id` must be valid **Community** node id
  + `/api/issue/value?filter_id=string[&user_id=string]` `filter_id` must be valid **Issue** node id
  + `/api/issue/objective?filter_id=string[&user_id=string]` `filter_id` must be valid **Issue** node id
  + `/api/issue/policy?filter_id=string[&user_id=string]` `filter_id` must be valid **Issue** node id

*  **URL Params**

   **Required:**
   `filter_id=[string]` For all endpoints except `/api/community`
   
   **Optional:**
   `user_id=[string]` For `/api/issue/(value|policy|ojective)` endpoints, a `user_id` parameter can be included
   to only return nodes ranked by that user.
  

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** `{ nodes : [ { id : [integer], ... }, ... ] }`
 
* **Error Response:**

  * **Code:** 422 UNPROCESSABLE ENTITY <br />
    **Cause:** Invalid request parameters


**Rank an Entity**
----
  Assign rank as user to a given entity `Issue|Value|Objective|Policy`.

* **Method:**
  
  `POST`

* **URL**

  + `/api/rank/issue`
  + `/api/rank/value`
  + `/api/rank/objective`
  + `/api/rank/policy` 

* **Data Params**

  ```
  {
    user_id:    [string],
    node_id:    [string],  // must be valid `Value|Objective|Policy|Issue` node
    issue_id:   [string],  // not required if node to be ranked is of type `Issue` 
    rank:       [integer]
  }
  ```
  
* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:**
    
    ```
    {
      success:  [boolean],
      error:    [string]    // present if success == False
    }
    ```

* **Error Response:**

  * **Code:** 422 UNPROCESSABLE ENTITY <br />
    **Cause:** Invalid request parameters


**Map two Entities**
----
  Create a user map between two entities `Value->Objective|Objective->Policy`.

* **Method:**
  
  `POST`

* **URL**

  + `/api/map/value/objective`
  + `/api/map/objective/policy`

* **Data Params**

  ```
  {
    user_id:    [string],
    src_id:     [string],
    dst_id:     [string],
    strength:   [integer]
  }
  ```
  
* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:**

    ```
    {
      success:  [boolean],
      error:    [string]    // present if success == False
    }
    ```
 
* **Error Response:**

  * **Code:** 422 UNPROCESSABLE ENTITY <br />
    **Cause:** Invalid request parameters


**Generate summary for stacked bar chart visualization**
----
  Summarize ranking of likert responses of all users for a specific `Value|Objective|Policie` in context of an issue. 
  
* **Method:**
  
  `GET`  
  
* **URL**

  + `/api/summary/value`
  + `/api/summary/objective`
  + `/api/summary/policy`

*  **URL Params**

   **Required:**
   `issue_id=[string]`

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** <br />
    
    ```
    {
        success : True|False
        invalid : [invalid rank, ... , invalid rank],    // any values not in likert scale
        data : {
            node_id : {
                name: <node name>,
                data: [ SD count, D count, N count, A count, SA count ]
            },
            ... ,
            node_id : {
                name: <node name>,
                data: [ SD count, D count, N count, A count, SA count ]
            }
        }
        error : "error message" // only present if success == False
    }
    ```
 
* **Error Response:**

  * **Code:** 422 UNPROCESSABLE ENTITY <br />
    **Cause:** Invalid request parameters


