#OpenBadge API -- The working bits

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

In general Headers are used exclusively for Authentication, either via a `X-GODKEY` for God-level
endpoints, or by the `badgeID` (ng-Device's `uuid`). The exeption to this is in `GET`'s, which 
sometimes use headers to specify what is to be gotten.






##Endpoints
####Project Level Endpoints
Method                |        Path            | Summary                       | Accessible To
----------------------|------------------------|-------------------------------|------------------------------
[GET](#getproject)    | /projects              | get project's badges/members  | Project's Hubs

####Meeting Level Endpoints
Method                |        Path            | Summary                       | Accessible To
----------------------|------------------------|-------------------------------|------------------------------
[PUT](#putmeeting)    | /:projectID/meetings   | initialize a meeting          | Project's Hubs
[GET](#getmeeting)    | /:projectID/meetings   | get the meetings for a project| Project's Hubs
[POST](#postmeeting)  | /:projectID/meetings   | add data to a meeting        | Project's Hubs


####Hub Level Endpoints
Method                |        Path            | Summary                       | Accessible To
----------------------|------------------------|-------------------------------|------------------------------
[PUT](#puthub)        | /:anyNumber/hubs       | add hub to defualt project    | All    
[GET](#gethub)        | /:projectID/hubs       | get hub's metadata and projects| Project's Hubs











##Project Level Endpoints

<a name="getproject"></a>
###GET /projects

Get badge ownership info and `project_id` for a hub

**Headers Passed**

Key          | Type    |
-------------|---------|
X-HUB-UUID   | text    |

*Response Codes*
- 200 - got project info
- 404 - hubID not found?

**Returned JSON**

```json
{
  "project_id": 3,
  "name": "Human Dynamics Main",
  "members": {
    "Bill Gates": {
      "badge": "DB:C8:1B:F8:B8:0F",
      "name": "Bill Gates",
      "id": 9
    },
    "Jackson Kearl": {
      "badge": "D2:3C:F6:B9:87:24",
      "name": "Jackson Kearl",
      "id": 5
    },
    "Cynthia Zhou": {
      "badge": "FA:DF:C3:8C:99:3C",
      "name": "Cynthia Zhou",
      "id": 7
    },
    "Oren Lederman": {
      "badge": "E3:09:E5:88:38:B2",
      "name": "Oren Lederman",
      "id": 6
    },
    "Steve Jobs": {
      "badge": "F2:74:78:84:E2:76",
      "name": "Steve Jobs",
      "id": 8
    }
  },
  "badge_map": {
    "FA:DF:C3:8C:99:3C": {
      "name": "Cynthia Zhou",
      "key": "EE2FRYT3LT"
    },
    "E3:09:E5:88:38:B2": {
      "name": "Oren Lederman",
      "key": "Z01MPNJJ9Y"
    },
    "F2:74:78:84:E2:76": {
      "name": "Steve Jobs",
      "key": "XBACZK85G6"
    },
    "DB:C8:1B:F8:B8:0F": {
      "name": "Bill Gates",
      "key": "PC8FI0C9IU"
    },
    "D2:3C:F6:B9:87:24": {
      "name": "Jackson Kearl",
      "key": "0R4PW5FXP5"
    }
  }
}
```




















##Meeting Level Endpoints


<a name="putmeeting"></a>
###PUT /:projectID/meetings

Create a meeting with given logfile.

**Headers Passed**

Key          | Type    |
-------------|---------|
X-HUB-UUID   | text    |


**Passed FILE**
```json
{"uuid":"12345","start_time":"2016-07-02T15:31:07.767Z","location":"meetingroom","type":"study","description":""}
//chunk data
```

*Response Codes*
- 200 - meeting created
- 401 - hub doesn't belong to project
- 404 - hubUUID not found

**Returned JSON**

```json
{
  "details": "meeting created"
}
```




<a name="getmeeting"></a>
###GET /:projectID/meetings

Get all meetigns in a project, with or without thier respective files. 

If X-GET-FILES.lower() is equal to "true", this will return a UUID-accessible Associated Array of metadata and chunk
as separate entries in a dictionary. Otherwise, it will return a UUID-accessible Associated Array of metadata objects

**Headers Passed**

Key          | Type    |
-------------|---------|
X-HUB-UUID   | text    |
X-GET-FILES  | text    |


*Response Codes*
- 200 - got meetings
- 401 - hub doesn't belong to project
- 404 - hubUUID not found

**Returned JSON**

```json
{
  "meetings": {
    "c65c943da5487d51_1468987120250": {
      "metadata": {
        "group": "Explore",
        "uuid": "c65c943da5487d51_1468987120250",
        "showVisualization": true,
        "timestamp": 1468987120.25,
        "start_time": "2016-07-20T03:58:40.250Z",
        "last_log_serial": 0,
        "moderator": "none",
        "location": "meetingroom",
        "members": [
          "0R4PW5FXP5",
          "Z01MPNJJ9Y",
          "PC8FI0C9IU"
        ],
        "last_log_time": 1468987120.264,
        "type": "study",
        "description": ""
      }
    },
    "c65c943da5487d51_1468988149042": {
      "metadata": {
        "group": "Explore",
        "uuid": "c65c943da5487d51_1468988149042",
        "showVisualization": true,
        "timestamp": 1468988149.042,
        "start_time": "2016-07-20T04:15:49.042Z",
        "last_log_serial": 0,
        "moderator": "none",
        "location": "meetingroom",
        "members": [
          "Z01MPNJJ9Y",
          "XBACZK85G6",
          "EE2FRYT3LT",
          "0R4PW5FXP5",
          "PC8FI0C9IU"
        ],
        "last_log_time": 1468988149.047,
        "type": "study",
        "description": ""
      }
    },
    "c65c943da5487d51_1468983088679": {
      "metadata": {
        "group": "Explore",
        "uuid": "c65c943da5487d51_1468983088679",
        "showVisualization": true,
        "timestamp": 1468983088.679,
        "start_time": "2016-07-20T02:51:28.679Z",
        "last_log_serial": 0,
        "moderator": "none",
        "location": "meetingroom",
        "members": [
          "EE2FRYT3LT",
          "0R4PW5FXP5"
        ],
        "last_log_time": 1468983088.691,
        "type": "study",
        "description": ""
      }
    },
    "c65c943da5487d51_1468987429694": {
      "metadata": {
        "group": "Explore",
        "uuid": "c65c943da5487d51_1468987429694",
        "showVisualization": true,
        "timestamp": 1468987429.694,
        "start_time": "2016-07-20T04:03:49.694Z",
        "last_log_serial": 0,
        "moderator": "none",
        "location": "meetingroom",
        "members": [
          "EE2FRYT3LT",
          "0R4PW5FXP5",
          "Z01MPNJJ9Y"
        ],
        "last_log_time": 1468987429.708,
        "type": "study",
        "description": ""
      }
    }
  }
}
```








<a name="postmeeting"></a>
###POST /:projectID/meetings

Add chunks to a meeting

**Headers Passed**

Key          | Type    |
-------------|---------|
X-HUB-UUID  | text    |


**Passed JSON**
```json
["{"uuid":"12345","start_time":"2016-07-02T15:31:07.767Z","location":"meetingroom","type":"study","description":""}", ...
//chunk data as JSON'd list of JSON'd objects
]
```

*Response Codes*
- 200 - chunks added


**Returned JSON**

```json
{
  "details": "data added"
}
```


















##Hub Level Endpoints

<a name="puthub"></a>
###PUT /:anyNumber/hubs

Create a hub in the default project.

**Headers Passed**

Key          | Type    |
-------------|---------|
X-APP-UUID   | text    |


*Response Codes*
- 200 - hub created
- 400 - bad request (no UUID?)
- 500 - bad UUID, already registered?


<a name="gethub"></a>
###GET /:projectID/hubs

Get hub's name and meetings.

**Headers Passed**

Key          | Type    |
-------------|---------|
X-HUB-UUID   | text    |


*Response Codes*
- 200 - got hub data
- 401 - hub doesn't belong to project
- 404 - hubUUID not found

**Returned JSON**

```json
{
  "meetings": {
    "12345": {"last_log_timestamp": some UNIX now-epoch int,
              "last_log_serial": 43,
              "is_complete": T/F
  },
  "name": "East Conference Room"
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