// Copyright 2023 The FreePDM team. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found in the LICENSE file.

package filesystem

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"path"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/grd/FreePDM/src/config"
	ex "github.com/grd/FreePDM/src/extras"
)

// LockedIndex is the list of locked files
type LockedIndex struct {
	fileNr   int64  // The number of the file
	version  int16  // The number of the version
	userName string // Who checked this file out
}

// File System related Class
type FileSystem struct {
	index             FileIndex
	vaultDir          string
	mainPdmDir        string
	vaultUid          int
	user              string
	userUid           int
	currentWorkingDir string
	lockedCvs         string
	lockedIndex       []LockedIndex
}

const LockedFileCsv = "LockedFiles.csv"

// Constructor
func InitFileSystem(vaultDir, userName string) (self FileSystem) {
	self = FileSystem{vaultDir: vaultDir, user: userName}
	self.mainPdmDir = path.Join(self.vaultDir, "PDM")
	self.currentWorkingDir = self.mainPdmDir
	self.vaultUid = config.GetUid("vault")
	self.userUid = config.GetUid(userName)

	if self.userUid == -1 {
		log.Fatal("Username has not been stored into the FreePDM config file. Please follow the setup process.")
	}

	self.index = InitFileIndex(self.vaultDir, self.userUid, self.vaultUid)

	self.lockedCvs = path.Join(self.vaultDir, LockedFileCsv)
	self.ReadLockedIndex() // retrieve the values

	os.Chdir(self.currentWorkingDir)

	log.Printf("Vault dir: %s", self.currentWorkingDir)

	return self
}

// Updates the locked index by reading from the lockedTxt file.
func (self *FileSystem) ReadLockedIndex() {

	file, err := os.Open(self.lockedCvs)
	ex.CheckErr(err)
	defer file.Close()

	r := csv.NewReader(file)

	records, err := r.ReadAll()

	ex.CheckErr(err)

	self.lockedIndex = make([]LockedIndex, 0, len(records)*2)
	var list = LockedIndex{}

	for _, record := range records {

		list.fileNr = ex.Atoi64(record[0])
		list.version = ex.Atoi16(record[1])
		list.userName = record[2]

		self.lockedIndex = append(self.lockedIndex, list)
	}
}

func (self *FileSystem) WriteLockedIndex() {

	records := [][]string{
		{"FileNumber", "Version", "UserNume"},
	}

	for _, list := range self.lockedIndex {

		records = append(records, []string{
			ex.I64toa(list.fileNr),
			ex.I16toa(list.version),
			list.userName})

	}

	file, err := os.OpenFile(self.lockedCvs, os.O_WRONLY|os.O_CREATE, 0644)
	// file, err := os.Open(self.lockedCvs)
	ex.CheckErr(err)
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	err = writer.WriteAll(records) // calls Flush internally
	ex.CheckErr(err)

	err = os.Chown(self.lockedCvs, self.userUid, self.vaultUid)
	ex.CheckErr(err)
}

// import a file inside the PDM. When you import a file the meta-data also gets imported,
// which means uploaded to the server.
// When you import a file or files you are placing the new file in the current directory.
// The new file inside the PDM gets a revision number automatically.
// The function returns the number of the imported file.
func (self *FileSystem) ImportFile(fname string) int64 {
	// check wether a file exist
	if ex.FileExists(fname) == false {
		log.Fatalf("File %s could not be found.", fname)
	}

	idx := len(self.mainPdmDir) + 1 // trailing slash

	dirname := self.currentWorkingDir[idx:] // takes away the mainPdmDir part

	// storing "fname" and "dir" into the file index
	index := self.index.AddItem(fname, dirname)

	dir := fmt.Sprintf("%d", index)

	// fd := InitFileDirectory(self, path.Join(self.mainPdmDir, dir))
	fd := InitFileDirectory(self, dir)

	fd.NewDirectory().ImportNewFile(fname)

	log.Printf("Imported %s into %s with version %d\n", fname, self.index.FileNameOfString(fd.dir), 0)

	// Checking out the new file so no one else can see it.

	err := self.CheckOut(index, 0)
	ex.CheckErr(err)

	return index
}

// Generates a new version of a file and returns the version number.
func (self *FileSystem) NewVersion(indexNr int64) int16 {

	dirIdx, err := self.index.DirIndex(indexNr)
	ex.CheckErr(err)
	dir := path.Join(self.mainPdmDir, dirIdx)

	fd := InitFileDirectory(self, dir)

	ret := fd.NewVersion()

	// Checking out the new file so no one else can see it.

	log.Printf("Created version %d of file %s\n", ret, self.index.FileName(indexNr))

	err = self.CheckOut(indexNr, ret)
	ex.CheckErr(err)

	return ret
}

// Creates a new directory inside the current directory, with the correct uid and gid.
func (self FileSystem) Mkdir(dname string) error {

	// Check wether dname is an int. We don't want that, because the number could interfere with the fileindex.
	if _, err := strconv.Atoi(dname); err == nil {
		return fmt.Errorf("Please change %s into a string, now it is a number.", dname)
	}

	err := os.Mkdir(dname, 0777)
	ex.CheckErr(err)

	err = os.Chown(dname, self.userUid, self.vaultUid)
	ex.CheckErr(err)
	return nil
}

func (self *FileSystem) Chdir(dir string) {
	newPath := filepath.Clean(path.Join(self.currentWorkingDir, dir))
	self.currentWorkingDir = newPath
	err := os.Chdir(self.currentWorkingDir)
	ex.CheckErr(err)
}

// list the sorted directories and files of the current working directory.
func (self FileSystem) ListWD() []FileInfo {
	return self.ListDir(self.currentWorkingDir)
}

// list the sorted directories and files, as long as the directory is inside the vault.
func (self FileSystem) ListDir(dirName string) []FileInfo {
	dir_list, err := os.ReadDir(dirName)
	ex.CheckErr(err)
	directoryList := make([]FileInfo, len(dir_list)+1)
	fileList := make([]FileInfo, len(dir_list))
	subDirList := make([]FileInfo, len(dir_list))

	for _, sub_dir := range dir_list {
		if num, err := strconv.Atoi(sub_dir.Name()); err == nil { //TODO verder invullen...
			// dir := filepath.Join(self.currentWorkingDir, self.index.Dir(self.index.indexNumberTxt))
			// fd := InitFileDirectory(self, dir)
			fileList = append(directoryList, FileInfo{
				Dir:      false,
				FileName: self.index.FileName(int64(num)),
			})
		} else {
			directoryList = append(directoryList, FileInfo{Dir: true, FileName: sub_dir.Name()})
		}
	}

	if path.Clean(dirName) != self.mainPdmDir {
		subDirList = append(subDirList, FileInfo{Dir: true, FileName: ".."})
	}

	subDirList = append(subDirList, directoryList...)
	subDirList = append(subDirList, fileList...)

	return subDirList
}

// returns the latest version number of a file in the current
// directory or -1 when the file doesn't exist.
func (self FileSystem) CheckLatestFileVersion(fname string) int64 {
	file_list, err := os.ReadDir(".")
	ex.CheckErr(err)
	var result int64 = -1
	for _, file := range file_list {
		if ex.DirExists(file.Name()) {
			continue
		}
		file1, ext1 := SplitExt(file.Name())
		if fname == file1 {
			n, err := strconv.ParseInt(ext1[1:], 10, 64)
			ex.CheckErr(err)
			result = n
		}
	}

	return result
}

// Check whether the itemnr is locked.
// Returns the name of the user who locked it or empty when not locked.
func (self FileSystem) IsLocked(itemNr int64, ver int16) string {

	for _, item := range self.lockedIndex {
		if item.fileNr == itemNr && item.version == ver {
			return item.userName
		}
	}

	return "" // Nothing found
}

// Checkout means locking a itemnr so that only you can use it.
func (self *FileSystem) CheckOut(itemNr int64, ver int16) error {

	self.ReadLockedIndex() // update the index

	// Set file mode 0700

	dir, err := self.index.DirIndex(itemNr)
	ex.CheckErr(err)

	fd := InitFileDirectory(self, path.Join(self.mainPdmDir, dir))
	fd.OpenItemVersion(ver)

	// check whether the itemnr is locked

	if usr := self.IsLocked(itemNr, ver); usr != "" {

		return fmt.Errorf("File %d-%d is locked by user %s.", itemNr, ver, usr)

	} else {

		self.lockedIndex = append(self.lockedIndex, LockedIndex{itemNr, ver, self.user})

		// Appending to file

		var record = make([]string, 3)

		record[0] = ex.I64toa(itemNr)
		record[1] = ex.I16toa(ver)
		record[2] = self.user

		addRecord(self.lockedCvs, record)

		log.Printf("Checked out version %d of file %s\n", ver, self.index.FileName(itemNr))

		return nil
	}
}

// Checkin means unlocking an itemnr.
// The description and long description are meant for storage.
func (self *FileSystem) CheckIn(itemNr int64, ver int16, descr, longdescr string) error {

	// Set file mode 0755

	dir, err := self.index.DirIndex(itemNr)
	ex.CheckErr(err)

	fd := InitFileDirectory(self, path.Join(self.mainPdmDir, dir))

	fd.StoreData(ver, descr, longdescr)

	fd.CloseItemVersion(ver)

	// check whether the itemnr is locked

	usr := self.IsLocked(itemNr, ver)

	if usr != self.user {

		return fmt.Errorf("File %d-%d is locked by user %s.", itemNr, ver, usr)

	} else {

		// Remove item from index

		var nr int
		for i, y := range self.lockedIndex {
			if y.fileNr == itemNr && y.version == ver {
				nr = i
			}
		}

		self.lockedIndex = append(self.lockedIndex[:nr], self.lockedIndex[nr+1:]...)

		self.WriteLockedIndex()

		log.Printf("Checked in version %d of file %s", ver, self.index.FileName(itemNr))

		return nil
	}
}

// TODO right now this feature doesn't work.

// Rename a directory or a file, for instance when the user wants to use a file
// with a specified numbering system.
func (self *FileSystem) Rename(src, dest string) error {

	// TODO Check wether "dest" doesn't exist

	// and ater that renames the file inside the file index.

	err := self.index.renameItem(src, dest)
	ex.CheckErr(err)

	// Rename the file from src to dest

	dir, err := self.index.Dir(src)
	ex.CheckErr(err)

	fd := InitFileDirectory(self, path.Join(self.currentWorkingDir, dir))
	err = fd.fileRename(src, dest)

	return nil
}

// TODO right now this feature doesn't work

// Moves a file to a different directory.
func (self *FileSystem) Move(fileName, destDir string) error {

	// delete the part up to PDM dir from destDir

	dir := destDir
	if strings.HasPrefix(destDir, self.mainPdmDir) {
		destDir = destDir[len(self.mainPdmDir):]
	}

	// Move file in FileIndex

	self.index.moveItem(fileName, dir)

	// Move file

	fname, err := self.index.Dir(fileName)
	ex.CheckErr(err)
	err = os.Rename(fname, destDir)
	ex.CheckErr(err)
	err = os.Chown(destDir, self.userUid, self.vaultUid)
	ex.CheckErr(err)

	return nil
}

func SplitExt(path string) (root, ext string) {
	ext = filepath.Ext(path)
	root = path[:len(path)-len(ext)]
	return
}
