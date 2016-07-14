#API

##Overview
The basic idea in this backend is that there should be only one way to do anything. 
This sometimes means requiring two or more API calls for something that ought to take
one, but it is my belief that this makes it simpler. The exception to this is in first creation
of a project, where one may supply the hubs and badges to initialize, skipping over 
the `PUT /:projectID/hubs` and `PUT /:projectID/badges` endpoints.

All standard connections will start with a `GET` to `/projects`, and henceforth 
use the `projectID` returned by that request to communicate with the server, in the form of
`PUT`'s, `GET`'s, and `POST`'s to `/:projectID/[meetings, hubs, badges]`

There exist a collection of `God` level endpoints. These require a special key that will
not be available to any hubs meant for use by the end user. All other endpoints are restricted
to hubs that are members of the project being accessed. 

In general Headers are used exclusively for Authentication, either via a `GodKey` for God-level
endpoints, or by the `badgeID` (ng-Device's `uuid`). The exeption to this is in `GET`'s, which 
sometimes use headers to specify what is to be gotten.






##Endpoints
####Project Level Endpoints
Method                |        Path            | Summary                       | Protection Level   | Status
----------------------|------------------------|-------------------------------|--------------------|-------------
[PUT](#putproject)    | /projects              | create a project w/ given data| God                | None
[GET](#getproject)    | /projects              | get project's badges/members  | None               | Implemented

####Meeting Level Endpoints
Method                |        Path            | Summary                       | Protection Level   | Status    
----------------------|------------------------|-------------------------------|--------------------|-------------
[PUT](#putmeeting)    | /:projectID/meetings   | initialize a meeting          | Project's Hubs     | Implemented
[GET](#getmeeting)    | /:projectID/meetings   | get last update's timestamp   | Project's Hubs     | None
[POST](#postmeeting)  | /:projectID/meetings   | upload meeting logs           | Project's Hubs     | None *


####Hub Level Endpoints
Method                |        Path            | Summary                       | Protection Level   | Status
----------------------|------------------------|-------------------------------|--------------------|-------------
[PUT](#puthub)        | /:projectID/hubs       | add hub to project            | God                | None
[GET](#gethub)        | /:projectID/hubs       | get hub's data (w/ viz range?)| Project's Hubs     | Implemented
[POST](#posthub)      | /:projectID/hubs       | change hub's name/desc/etc.   | God                | None

####Badge Level Endpoints
Method                |        Path            | Summary                       | Protection Level   | Status
----------------------|------------------------|-------------------------------|--------------------|-------------
[PUT](putbadge)       | /:projectID/badges     | add badge(s) to project       | God                | None
[GET](#getbadge)      | /:projectID/badges     | get name/project for badge    | God                | None
[POST](#getbadge)     | /:projectID/badges     | change name associated w badge| Project's Hubs     | None













##Project Level Endpoints

<a name="putproject"></a>
###PUT /projects

Creates a new project with given name, hubs, and badges, returning the created (unique) `projectID`.

**Headers Passed**

Key        | Type    |
-----------|---------|
X-GODKEY   | text    |

**Passed JSON**

```json 
{
    "name":"Apple, Inc.",
    "hubs": 
    [
        {"name":"West Conference", "uuid":"341fef..."},
        {"name":"East Conference", "uuid":"gug455..."},
         ...
    ],
    "badges": 
    [
        {"name":"Steve Jobs", "uuid":"guhwe..."},
        {"name":"Tim Cook", "uuid":"grege..."},
         ...
    ]
}
```
                
                

*Response Codes*
- 201 - project was created
- 403 - forbidden (not god?)


**Returned JSON**
```json
{
  "status": "success",
  "details": "project added",
  "projectID": "eyJ0eXAiOiJKV1..."
}
```


<a name="getproject"></a>
###GET /projects

Get badge ownership info and `projectID` for a hub

**Headers Passed**

Key          | Type    |
-------------|---------|
X-HUB-UUID   | text    |

*Response Codes*
- 200 - got project info
- 404 - hub not found

**Returned JSON**

```json
{
  "name": "Amazon",
  "project_id": 2,
  "badge_map": {
    "7": "Amazon.com",
    "8": "IMDB",
    "9": "Zappos"
  },
  "members": [
    {
      "badge": "7",
      "name": "Amazon.com",
      "key": "U5KUR996VZ",
      "id": 4
    },
    {
      "badge": "8",
      "name": "IMDB",
      "key": "8QZ1MY119K",
      "id": 5
    },
    {
      "badge": "9",
      "name": "Zappos",
      "key": "RZZU2SWK4M",
      "id": 6
    }
  ]
}
```




















##Meeting Level Endpoints


<a name="putmeeting"></a>
###PUT /:projectID/meetings

Create a meeting with given logfile.

**Headers Passed**

Key          | Type    |
-------------|---------|
hubID        | text    |


**Passed JSON**
```json
{
    "log":
    [
        {"meetingID":"2016-07-02T15:31:07.767Z","showVisualization":true}
        // optional log lines... 
    ]
}
```

*Response Codes*
- 201 - meeting created
- 401 - unauthorized (bad hubID?)

**Returned JSON**

```json
{
  "status": "success",
  "details": "meeting created",
  "lastData":"2016-07-02T15:31:07.767Z"
}
```

<a name="getmeeting"></a>
###GET :projectID/meetings

Get the timestamp of the last received log.

**Headers Passed**

Key          | Type    |
-------------|---------|
hubID        | text    |
meetingID    | date    |

*Response Codes*
- 200 - got stamp
- 401 - unauthorized (bad hubID?)
- 500 - server error (no meeting found?)

**Returned JSON**

```json
{
  "status": "success",
  "details": "last data found",
  "lastData":"2016-07-02T15:39:27.767Z"
}
```

<a name="postmeeting"></a>
###POST /:projectID/meetings

Upload log data to the server

**Headers Passed**

Key          | Type    |
-------------|---------|
hubID        | text    |




**Passed JSON**

```json
{
    "meetingID":"2016-07-02T15:31:07.767Z",
    "logs": 
    [
        // log lines....
    ]
```

*Response Codes*
- 202 - uploaded log
- 403 - unauthorized (bad hubID?)
- 500 - server error (no meeting found?)

**Returned JSON**

```json
{
  "status": "success",
  "details": "uploaded logs"
}
```

























##Hub Level Endpoints


<a name="puthub"></a>
###PUT /:projectID/hubs

Create a hub for the given `projectID`.

**Headers Passed**

Key          | Type    |
-------------|---------|
GodKey       | text    |


**Passed JSON**
```json
{
    "name":"North Conference Room",
    "description":"iPhone hub located in the north conference room",
    "vizualizationRanges":[{"start":0, "end":45}, {"start":90,"end":180}],
    "uuid":"fwefhewfh8ew"
}
```

*Response Codes*
- 201 - hub created
- 403 - forbidden (bad GodKey?)

**Returned JSON**

```json
{
  "status": "success",
  "details": "hub created",
}
```


<a name="gethub"></a>
###GET :projectID/hubs

Get hubs visualization ranges, name, description, etc.

**Headers Passed**

Key          | Type    |
-------------|---------|
hubID        | text    |


*Response Codes*
- 200 - got hub data
- 401 - unauthorized (bad hubID?)

**Returned JSON**

```json
{
  "status": "success",
  "details": "hub data found",
  "name":"South Conference Room",
  "description":"iPhone hub located in the south conference room",
  "vizualizationRanges":[{"start":0, "end":45}, {"start":90,"end":180}]
}
```

<a name="posthub"></a>
###POST /:projectID/hubs

Edit/Update Hub name/description. Possibly Viz ranges as well. 

**Headers Passed**

Key          | Type    |
-------------|---------|
GodKey       | text    |




**Passed JSON**

```json
{
    "uuid":"hg9843hf43",
    "name":"West Conference",
    "description":"Andriod in WC",
    // maybe viz ranges
}
```

*Response Codes*
- 200 - updated hub
- 403 - Forbidden (bad GodKey?)
- 500 - server error (no hub found?)

**Returned JSON**

```json
{
  "status": "success",
  "details": "updated hub"
}
```






























##Badge Level Endpoints


<a name="putbadge"></a>
###PUT /:projectID/badges

Add a badge to a project.


**Headers Passed**

Key          | Type    |
-------------|---------|
GodKey       | text    |


**Passed JSON**
```json
{
    "projectID":"wegifhuwhe",
    "badegeID":"2apoihef",
    "name":"Johnny Ive"
}
```

*Response Codes*
- 201 - badge created
- 403 - forbidden (bad GodKey?)

**Returned JSON**

```json
{
  "status": "success",
  "details": "badge created"
}
```

<a name="getbadge"></a>
###GET :projectID/badges

Get the name and project associated with a given badge.

**Headers Passed**

Key          | Type    |
-------------|---------|
GodKey       | text    |
badgeID      | text    |



*Response Codes*
- 200 - got badge details
- 401 - unauthorized (bad hubID?)
- 500 - server error (no meeting found?)

**Returned JSON**

```json
{
  "status": "success",
  "details": "badge found",
  "name":"Steve Jobs",
  "projectID":"84hgfieg",
  "projectName":"Apple Inc."
}
```

<a name="postbadge"></a>
###POST /:projectID/badges

Change the name associated with a given badge. 

**Headers Passed**

Key          | Type    |
-------------|---------|
hubID        | text    |




**Passed JSON**

```json
{
    "badegeID":"2016-07-02T15:31:07.767Z",
    "newName":"Tim Cook"
}
```

*Response Codes*
- 200 - updated name
- 403 - unauthorized (bad hubID?)
- 500 - server error (no badge found?)

**Returned JSON**

```json
{
  "status": "success",
  "details": "updated badge"
}
```





















##Documentation Format
####(courtesy of [Conner DiPaolo](https://github.com/cdipaolo))

Keep documentation in this format please!

Add the method to the [path overview](#paths) and place it under the correct [section](#sections)

```markdown
<a name="briefname"></a>
###METHOD /path/to/endpoint

put a decent description of what the endpoint does here

**Headers Passed**

Key   | Type    | Description
------|---------|------------
key   | string  | here's a header description

**Passed JSON**
{
  "example":"of",
  "passed":"json",
  "goes":{
    "here":true
  }
}


*Response Codes*
- 400 - invalid request
- 200 - OK
- 201 - thing was created
- 401 - unauthorized

**Returned JSON**
{
  "example":"of",
  "return":"json",
  "goes":{
    "here":true
  }
}

#####Comments

put notes here about, for example, optional parameters and/or specific types

```