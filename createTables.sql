-- Entries made by hand except possibly monitorStart, monitorEnd and status

CREATE TABLE IF NOT EXISTS FileRoot
( id int NOT NULL AUTO_INCREMENT,
  dir varchar(255) NOT NULL,
  nickname      varchar(255) NOT NULL COMMENT 'Need not be unique',
  version       varchar(255) NOT NULL DEFAULT '',
  production    tinyint      NOT NULL DEFAULT '1' COMMENT 'maybe not useful',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_cs COMMENT='Configuration for a measurement';

CREATE TABLE IF NOT EXISTS Measurement
( id int NOT NULL AUTO_INCREMENT,
  fileRootId    int NOT NULL,
  status        enum('PENDING','ACTIVE','COMPLETE','FAILED') NOT NULL DEFAULT 'PENDING',
  monitorStart  timestamp NULL,
  monitorEnd    timestamp NULL,
  monitorPeriod int          NOT NULL DEFAULT '60' COMMENT 'In minutes',
  PRIMARY KEY (id),
  CONSTRAINT fkm01 FOREIGN KEY(fileRootId) REFERENCES FileRoot(id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Configuration for a measurement';

CREATE TABLE IF NOT EXISTS File
( id int NOT NULL AUTO_INCREMENT,
  fileRootId   int NOT NULL,
  relPath      varchar(255) NOT NULL  COMMENT 'rel to Measurement.rootDir',
  basename     varchar(255) NOT NULL,
  modifyTimeU  int  NOT NULL COMMENT 'seconds since Epoch',
  lastAccessU  int  NOT NULL COMMENT 'from first time file scanned',
  unused       int  NOT NULL COMMENT 'seconds from last access (at row insert time)',
  symlink      tinyint NOT NULL DEFAULT '0',
  monitorOn    tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (id),
  UNIQUE INDEX(relPath, fileRootId),
  CONSTRAINT fkf01 FOREIGN KEY(fileRootId) REFERENCES FileRoot(id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_cs COMMENT='Configuration for a measurement';

CREATE TABLE IF NOT EXISTS MappingFileMeas
( id int NOT NULL AUTO_INCREMENT,
  fileId int NOT NULL,
  measurementId int NOT NULL,
  PRIMARY KEY(id),
  CONSTRAINT fkmfm01 FOREIGN KEY(fileId) REFERENCES File(id),
  CONSTRAINT fkmfm02 FOREIGN KEY(measurementId) REFERENCES Measurement(id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Files belonging to measurement';
  
CREATE TABLE IF NOT EXISTS Stats
( id                int NOT NULL AUTO_INCREMENT,
  mappingFileMeasId int NOT NULL,
  lastAccessTS      timestamp  NOT NULL,
  lastAccessU       int NOT NULL COMMENT 'seconds since Epoch',
  changeTimeU       int NOT NULL COMMENT 'seconds since Epoch',
  accessCountToday  int NOT NULL DEFAULT '0',
  accessCountMonth  int NOT NULL DEFAULT '0',
  upTillToday       int NOT NULL DEFAULT '0' COMMENT 'access thru midnight',
  upTillMonth       int NOT NULL DEFAULT '0',
  accessCountTotal  int NOT NULL DEFAULT '0',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Data per (file, measurement) ';


