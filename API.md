#OpenBadge API -- The working bits

##Overview
The basic idea in this backend is that there should be only one way to do anything. 
This sometimes means requiring two or more API calls for something that ought to take
one, but it is my belief that this makes it simpler. Specifically, at the start
of the app, one should both GET projects and GT hubs, to get the long-term and 
temporal data respectively. 

All standard connections will start with a `GET` to `/projects`, and henceforth 
use the `projectKEY` returned by that request to communicate with the server, in the form of
`PUT`'s, `GET`'s, and `POST`'s to `/:projectKEY/[meetings, hubs, badges]`

In general Headers are used exclusively for Authentication, via the 
`X-BADGE_UUID` (ng-Device's `uuid`). The exception to this is in `GET`'s, which 
sometimes use headers to specify what is to be gotten.






##Endpoints
####Project Level Endpoints
Method                |        Path            | Summary                       | Accessible To
----------------------|------------------------|-------------------------------|------------------------------
[GET](#getproject)    | /projects              | get project's badges/members should need to be called only infrequently (when significant things change) | Project's Hubs

####Meeting Level Endpoints
Method                |        Path            | Summary                       | Accessible To
----------------------|------------------------|-------------------------------|------------------------------
[PUT](#putmeeting)    | /:projectKEY/meetings   | initialize a meeting          | Project's Hubs
[GET](#getmeeting)    | /:projectKEY/meetings   | get the meetings for a project, either just metadata -r whole file| Project's Hubs
[POST](#postmeeting)  | /:projectKEY/meetings   | add data to a meeting        | Project's Hubs


####Hub Level Endpoints
Method                |        Path            | Summary                       | Accessible To
----------------------|------------------------|-------------------------------|------------------------------
[PUT](#puthub)        | /:anyNumber/hubs       | add hub to default project    | All    
[GET](#gethub)        | /:projectKEY/hubs       | get hub's metadata and projects, and all othhr data that can change during a meeting (members, god-state, etc.)| Project's Hubs











##Project Level Endpoints

<a name="getproject"></a>
###GET /projects

Get badge ownership info and project identification info for a hub's project. 

**Headers Passed**

Key          | Type    |
-------------|---------|
X-HUB-UUID   | text    |

*Response Codes*
- 200 - got project info
- 404 - hubID not found

**Returned JSON**

```json
{
  "project_id": 1,
  "key": "O3KCU5CQXP",
  "name": "My Proj",
  "members": {
    "Jackson Kearl": {
      "badge": "6E:4A:85:C4:C2:87",
      "name": "Jackson Kearl",
      "id": 1
    },
    "Cynthia Zhou": {
      "badge": "7A:FF:38:51:0B:AC",
      "name": "Cynthia Zhou",
      "id": 3
    },
    "Oren Lederman": {
      "badge": "65:7D:D4:5D:9D:3B",
      "name": "Oren Lederman",
      "id": 2
    }
  },
  "badge_map": {
    "7A:FF:38:51:0B:AC": {
      "name": "Cynthia Zhou",
      "key": "K9VTVNXVVB"
    },
    "65:7D:D4:5D:9D:3B": {
      "name": "Oren Lederman",
      "key": "CCW9N7Y9B9"
    },
    "6E:4A:85:C4:C2:87": {
      "name": "Jackson Kearl",
      "key": "OSL86K9XGD"
    }
  }
}
```




















##Meeting Level Endpoints


<a name="putmeeting"></a>
###PUT /:projectKEY/meetings

Create a meeting with given logfile, or update the logfile of a given project. 

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

Get all meetings in a project, with or without their respective files. 

If X-GET-FILES is equal to "true", this will return a UUID-accessible Associated Array of metadata and events
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

Add chunks to a meeting. Will return with a `status: mismatch` if the logs
are not properly serial.

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

Get hub's name and meetings. If provided with an POSIX X-LAST-MEMBER-UPDATE, also get the 
members that have been added to this hub's project since last update,
as both a badge_map and list of members. Otherwise returns the full set of members.

**Headers Passed**

Key          | Type    |
-------------|---------|
X-HUB-UUID   | text    |
X-LAST-MEMBER-UPDATE | POSIX Timestamp |


*Response Codes*
- 200 - got hub data
- 401 - hub doesn't belong to project
- 404 - hubUUID not found

**Returned JSON**
Here, the X-LAST-MEMBER-UPDATE is such that 2 members are `new`.
```json
{
  "is_god": true,
  "meetings": {
    "c65c943da5487d51_1470636479534": {
      "last_log_timestamp": "1470636586.948",
      "last_log_serial": 110,
      "is_complete": true
    },
    "c65c943da5487d51_1470636747445": {
      "last_log_timestamp": "1470636829.338",
      "last_log_serial": 97,
      "is_complete": true
    }
  },
  "name": "Cyan Android",
  "members": {
    "D B": {
      "badge": "DB:C8:1B:F8:B8:0F",
      "name": "D B",
      "id": 17
    },
    "D 2": {
      "badge": "D2:3C:F6:B9:87:24",
      "name": "D 2",
      "id": 21
    }
  },
  "badge_map": {
    "DB:C8:1B:F8:B8:0F": {
      "name": "D B",
      "key": "31C60MMBJO"
    },
    "D2:3C:F6:B9:87:24": {
      "name": "D 2",
      "key": "FQGNXLRNCV"
    }
  }
}
```
Here, the X-LAST-MEMBER-UPDATE is such that no members are `new`.

```json
{
  "is_god": true,
  "meetings": {
    "c65c943da5487d51_1470636479534": {
      "last_log_timestamp": "1470636586.948",
      "last_log_serial": 110,
      "is_complete": true
    },
    "c65c943da5487d51_1470636747445": {
      "last_log_timestamp": "1470636829.338",
      "last_log_serial": 97,
      "is_complete": true
    }
  },
  "name": "Cyan Android",
  "members": {},
  "badge_map": {}
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