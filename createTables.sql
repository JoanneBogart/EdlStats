-- Entries made by hand except possibly monitorStart, monitorEnd and status

CREATE TABLE IF NOT EXISTS Fileroot
( id int NOT NULL AUTO_INCREMENT,
  dir varchar(255) NOT NULL,
  nickname      varchar(255) NOT NULL COMMENT 'Need not be unique',
  version       varchar(255) NOT NULL DEFAULT '',
  production    tinyint      NOT NULL DEFAULT '1' COMMENT 'maybe not useful',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_cs COMMENT='File hierarchy to examine';


CREATE TABLE IF NOT EXISTS File
( id int NOT NULL AUTO_INCREMENT,
  fileRootId   int NOT NULL,
  relPath      varchar(255) NOT NULL  COMMENT 'rel to FileRoot.dir',
  basename     varchar(255) NOT NULL,
  modifyTimeU  int  NOT NULL COMMENT 'seconds since Epoch',
  lastAccessU  int  NOT NULL COMMENT 'from first time file scanned',
  unused       int  NOT NULL COMMENT 'seconds from last access (at row insert time)',
  symlink      tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (id),
  UNIQUE INDEX(relPath, fileRootId),
  CONSTRAINT fkf01 FOREIGN KEY(fileRootId) REFERENCES FileRoot(id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_cs COMMENT='File to examine';

CREATE TABLE IF NOT EXISTS Widget
(id int NOT NULL AUTO_INCREMENT,
 edlName varchar(255) NOT NULL,
 pydmName varchar(255) NULL,
 PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_cs;

CREATE TABLE IF NOT EXISTS MappingFileWidget
(id int NOT NULL AUTO_INCREMENT,
 widgetId int NOT NULL,
 fileId   int NOT NULL,
 lineNumber int NOT NULL,
 PRIMARY KEY (id),
 CONSTRAINT fkmfw01 FOREIGN KEY(widgetId) REFERENCES Widget(id),
 CONSTRAINT fkmfw02 FOREIGN KEY(fileId) REFERENCES File(id),
 CONSTRAINT ui01 UNIQUE INDEX (fileId,widgetId,lineNumber)
 
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


