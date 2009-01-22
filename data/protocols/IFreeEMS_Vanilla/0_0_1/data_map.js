{
	/* A formal definition of :		*/
	/* - What data is available		*/
	/* - How it can be accessed		*/
	/* - How it is structured		*/
	/* - How it to interpret it		*/
    "FreeEMS Interface Data Map": {
		/* A four part interface versioning scheme consisting of :				*/
		/* - Unique Identifier		Same across all versions of a given fork	*/
		/* - Major Version			Significant jumps in functionality			*/
		/* - Minor Version			Minor features or significant fixes			*/
		/* - Revision Number			Initial dev and minor fixes only			*/
        "Interface Version Unique Identifier":	"IFreeEMS Vanilla",
        "Interface Version Unique Major":		0,
        "Interface Version Unique Minor":		0,
        "Interface Version Unique Revision":	1,
		"Data Blocks": {
			"Block List By Name": ["VE Table Main", "VE Table Secondary", "VE Table Tertiary", "Lambda Table", "etc"],
			"Block Definition": {
				"Location ID": 0,
	            "Display Name": "VE Table Main",
				"Description": "The main volumetric efficiency table as used for normal fuel injection calculations",
				"Size In Bytes": 1024,
				"Chunks": {
	                "Chunk": {
						"Payload IDs": [6, 8, 20, 24, 53],
						"Location ID": 0,
	                    "Display Name": "VE Table Main",
						"Size In Bytes": 1024,
						"Offset In Bytes": 0,
						"Reply Packet Attributes": {
							"Packet Attribute": {
								"Name": "Maximum RPM Axis Length",
								"Type": "Unsigned Short",
								"Length": 1,
								"Length In Bytes": 2,
								"Offset In Bytes": 0
							},
							"Packet Attribute": {
								"Name": "Maximum Load Axis Length",
								"Type": "Unsigned Short",
								"Length": 1,
								"Length In Bytes": 2,
								"Offset In Bytes": 2
							},
							"Packet Attribute": {
								"Name": "Maximum Table Length",
								"Type": "Unsigned Short",
								"Length": 1,
								"Length In Bytes": 2,
								"Offset In Bytes": 4
							},
							"Packet Attribute": {
								"Name": "VE Table Main",
								"Type": "Structure",
								"Length": 1024,
								"Length In Bytes": 1024,
								"Offset In Bytes": 6
							}							
						}
						"Structure": {
							"Element"{
								"Name": "RPM Axis Length",
								"Type": "Unsigned Short",
								"Length": 1,
								"Length In Bytes": 2,
								"Offset In Bytes": 0
							},
							"Element"{
								"Name": "Load Axis Length",
								"Type": "Unsigned Short",
								"Length": 1,
								"Length In Bytes": 2,
								"Offset In Bytes": 2
							},							
							"Element"{
								"Name": "RPM Axis",
								"Type": "Unsigned Short Array",
								"Length": 27,
								"Length In Bytes": 54,
								"Offset In Bytes": 4
							},							
							"Element"{
								"Name": "Load Axis",
								"Type": "Unsigned Short Array",
								"Length": 21,
								"Length In Bytes": 42,
								"Offset In Bytes": 58
							},							
							"Element"{
								"Name": "Table",
								"Type": "Unsigned Short Array",
								"Length": 462,
								"Length In Bytes": 924,
								"Offset In Bytes": 100
							}							
						}
	                }
	            }
			}
        }
    }
}
