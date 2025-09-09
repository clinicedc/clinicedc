Specimen management
===================

Specimen management starts with a ``lab profile`` The lab profile is a container class for testing panels, aliquot types, and aliquot processing. The lab profile is linked to the specimen requisition submitted at the clinic level for tests such as FBC, LFT, etc. A single requisition is submitted per test panel. A panel has its own processing profile that defines the number, type and volume of primary tubes and the number and type of derivative aliquots to be created from the primary tube(s). For example, a requisition with the viral load panel might start with a 5ml whole blood primary tube and be processed into derivative aliquots; 2 of plasma and 4 of buffy coat.

When a requisition is submitted for the primary specimen, the processing profile for the panel is referenced to generate records for the the aliquots to be created. From the aliquot records, specimen labels are generated and specimen management begins.
