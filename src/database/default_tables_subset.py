#!/usr/bin python3
# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2022 by the FreePDM team
    :license:   MIT License.
"""

# https://stackoverflow.com/questions/54118182/sqlalchemy-not-creating-tables
# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html
from base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Boolean, Integer, Float, String, Date, Enum, LargeBinary
import default_enum

# https://dataedo.com/kb/data-glossary/what-is-metadata
# https://www.geeksforgeeks.org/difference-between-data-and-metadata/
# https://www.geeksforgeeks.org/metadata-in-dbms-and-its-types/


class PdmDocument(Base):
    """Class with SQL Document properties"""
    __tablename__ = 'documents'

    document_id = Column(Integer, primary_key=True)
    document_number = Column(Integer)  # or should this be a string?
    document_name = Column(String(32))
    document_description = Column(String(32))
    document_full_description = Column(String)
    document_filename = Column(String(253), nullable=False)  # Limit of current file systems
    # Auto calculate extension
    document_ext = Column(String(253), nullable=False)  # Total limit of filename and extension is 255
    # document_path = Column(String)  # should belongs to same path as described in item

    # relationships with other tables
    user_id = Column(Integer, ForeignKey("users.user_id"))  # One to One
    user = relationship("PdmUser", back_populates="documents")
    item_id = Column(Integer, ForeignKey("items.item_id"))  # Many to One
    item = relationship("PdmItem", back_populates="models")

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        return(f"PdmDocument(document_id={self.document_id!r}, document_number={self.document_number!r}, document_name={self.document_name!r}, document_description={self.document_description!r}, document_full_description={self.document_full_description!r}, document_filename={self.document_filename!r}, document_ext={self.document_ext!r})")


class PdmItem(Base):
    """Class with SQL Item properties"""
    __tablename__ = 'items'

    item_id = Column(Integer, primary_key=True)
    item_number = Column(String(16))  # Don't expect that numbers longer than 16 digits are needed
    item_name = Column(String(32))
    item_description = Column(String(32))
    item_full_description = Column(String)
    item_number_linked_files = Column(Integer)
    item_path = Column(String, nullable=False)
    # TODO: get image from Model. If there is no fileimage add default empty image.
    item_preview = Column(LargeBinary)  # Change when no image is available
    # item should be able to exist in multiple projects. but need a single store location

    # relationships with other tables
    user_id = Column(Integer, ForeignKey("users.user_id"))  # Many to one
    user = relationship("PdmUser", back_populates="items")  # Many to Many
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)  # Many to Many
    # One Item can have many Models OR Documenets
    models = relationship("PdmModel", back_populates="item")  # One to Many
    documents = relationship("PdmDocument", back_populates="item")  # One to Many
    # Material = relationship("PdmMaterial", back_populates="item", uselist=False)  # One to one
    # One item can have one material otherwise it is another Item...
    # purchasing = relationship("PdmPurchasing", back_populates="item", uselist=False)  # Many to Many

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        # ignore cross columns
        return(f"PdmItem(item_id={self.item_id!r}, tem_number={self.item_number!r}, item_name={self.item_name!r}, item_description={self.item_description!r}, item_full_description={self.item_full_description!r}, item_number_linked_files={self.item_number_linked_files!r}, item_path={self.item_path!r}, item_preview={self.item_preview!r})")


class PdmLibrary(Base):
    """Class with default SQL Library properties"""
    __tablename__ = 'libraries'

    library_id = Column(Integer, primary_key=True)
    library_name = Column(String(32))
    library_status = Column(Enum(default_enum.ProjectState))
    library_path = Column(String)

    # relationships with other tables
    libraries = relationship("PdmLibrary", secondary="user_library_product_link", back_populates="libraries")  # Many to Many

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        return(f"PdmProduct(product_id={self.product_id!r}, product_name={self.product_name!r}, product_status={self.product_status!r}, product_path={self.product_path!r})")


class PdmModel(Base):
    """Class with SQL Model properties"""
    __tablename__ = 'models'

    model_id = Column(Integer, primary_key=True)
    model_number = Column(Integer)  # or should this be a string?
    model_name = Column(String(32))
    model_description = Column(String(32))
    model_full_description = Column(String)
    model_filename = Column(String(253), nullable=False)  # Limit of current file systems
    # Auto calculate extension
    model_ext = Column(String(253), nullable=False)  # Total limit of filename and extension is 255
    # model_path = Column(String)  # should belongs to same path as described in item
    model_preview = Column(LargeBinary)  # Change when no image is available

    # relationships with other tables
    user_id = Column(Integer, ForeignKey("users.user_id"))  # One to One
    user = relationship("PdmUser", back_populates="models")
    item_id = Column(Integer, ForeignKey("items.item_id"))  # Many to One
    item = relationship("PdmItem", back_populates="models")
    # material = relationship("PdmMaterial", back_populates="model", uselist=False)  # Many to Many

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        return(f"PdmModel(model_id={self.model_id!r}, model_number={self.model_number!r}, model_name={self.model_name!r}, model_description={self.model_description!r}, model_full_description={self.model_full_description!r}, model_filename={self.model_filename!r}, model_ext={self.model_ext!r}, model_preview={self.model_preview!r})")


class PdmOrganization(Base):
    """Class with default SQL organizations properties"""
    __tablename__ = 'organizations'

    organization_id = Column(Integer, primary_key=True)
    organization_name = Column(String(32))

    # relationships with other tables
    users = relationship("PdmUsers", secondary="user_role_organization_link", back_populates="organizations")  # One to One to Many OR One to Many to Many
    products = relationship("PdmProducts", secondary="product_project_link", back_populates="projects")  # Many to Many

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        return(f"PdmOrganization(organization_id={self.organization_id!r}, organization_name={self.organization_name!r})")


class PdmPermission(Base):
    """Class with default SQL Permission properties"""
    __tablename__ = 'permissions'

    permission_id = Column(Integer, primary_key=True)
    permission_name = Column(String(32))
    # TODO: add privileges - Also how to

    # relationships with other tables
    role_id = Column(Integer, ForeignKey("roles.role_id"))  # Many to Many
    roles = relationship("PdmRole", secondary="role_permission_link", back_populates="roles")  # Many to Many

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        return(f"PdmPermission(permission_id={self.permission_id!r}, role_name={self.permission_name!r})")


class PdmProduct(Base):
    """Class with default SQL Product properties"""
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(32))
    product_status = Column(Enum(default_enum.ProjectState))
    product_path = Column(String)

    # relationships with other tables
    organization_id = relationship("PdmOrganization", secondary="product_organization_link", back_populates="organizations")  # Many to Many

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        return(f"PdmProduct(product_id={self.product_id!r}, product_name={self.product_name!r}, product_status={self.product_status!r}, product_path={self.product_path!r})")


class PdmRole(Base):
    """Class with default SQL Role properties"""
    __tablename__ = 'roles'

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(32))
    # TODO: add privileges - Also how to

    # relationships with other tables
    # One User can have one role in one organization
    # But every User can have multiple roles dependend of the organization
    user_id = Column(Integer, ForeignKey("users.user_id"))  # Many to Many to Many?
    users = relationship("PdmUser", secondary="user_role_organization_link", back_populates="roles")  # One to One to Many OR One to Many to Many

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        return(f"PdmRole(role_id={self.role_id!r}, role_name={self.role_name!r})")


class PdmUser(Base):
    """Class with default SQL User properties"""
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(30))
    user_first_name = Column(String(30))
    user_last_name = Column(String(30))
    user_full_name = Column(String)
    user_email_adress = Column(String, nullable=False)  # TODO: change to mail address
    # password = Column(String, nullable=False)  # Password need to be hashed otherwise don't addd
    user_phonenumber = Column(Integer)  # TODO: add phonenumber property
    user_department = Column(String)  # Enum optionally
    # user_aliases = []  # TODO: What to do with aliases

    # relationships with other tables
    roles = relationship("PdmRole", secondary="user_role_organization_link", back_populates="users")  # One to One to Many OR One to Many to Many
    projects = relationship("PdmProjects", secondary="user_project_link", back_populates="users")  # Many to Many
    # One user can Check-Out Many Items, Models, documents
    items = relationship("PdmItem", back_populates="user")  # One to Many
    models = relationship("PdmModel", back_populates="user")  # One to Many
    documents = relationship("PdmDocument", back_populates="user")  # One to Many

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        return f"PdmUser(user_id={self.user_id!r}, user_name={self.user_name!r}, user_first_name={self.user_first_name!r}, user_last_name={self.user_last_name!r}, user_full_name={self.user_full_name!r}, user_email_adress={self.user_email_adress!r}, user_phonenumber={self.user_phonenumber!r}, user_department={self.user_department!r})"

#
# relationships with other tables
#

class PdmProductLibraryItemLink(Base):
    """Association Table between Product, Library and Item"""
    __tablename__ = "Product_library_item_link"

    # TODO: Check if this is right method
    # Every Item belongs to a Product OR a Library
    product_id = Column("product_id", ForeignKey("products.product_id"), primary_key=True)
    library_id = Column("library_id", ForeignKey("libraries.library_id"), primary_key=True)
    item_id = Column("item_id", ForeignKey("items.item_id"), primary_key=True)

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        return(f"Pdm Library Product Item Association Table(library_id={self.library_id!r}, product_id={self.product_id!r}, item_id={self.item_id!r})")


class PdmProductOrganizationLink(Base):
    """Association Table between User and Project"""
    # https://www.pythoncentral.io/sqlalchemy-association-tables/
    __tablename__ = "product_organization_link"

    product_id = Column("product_id", ForeignKey("products.product_id"), primary_key=True)
    project_id = Column("Organization_id", ForeignKey("organizations.organization_id"), primary_key=True)

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        return(f"Pdm Product Organization Association Table(product_id={self.product_id!r}, organization_id={self.organization_id!r})")


class PdmRolePermissionLink(Base):
    """Association Table between Role and Permissions"""
    # https://www.pythoncentral.io/sqlalchemy-association-tables/
    __tablename__ = "user_role_link"

    role_id = Column("role_id", ForeignKey("roles.role_id"), primary_key=True)
    permission_id = Column("permission_id", ForeignKey("permissions.permission_id"), primary_key=True)

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        return(f"Pdm User Role Association Table(user_id={self.role_id!r}, role_id={self.permission_id!r})")


class PDMUserRoleOrganizationLink(Base):
    """Association Table between User and Project"""
    # https://www.pythoncentral.io/sqlalchemy-association-tables/
    __tablename__ = "user_role_organization_link"

    # TODO: Check if this is right method
    # Every Have a Role Within a Organization. A user can be part of multple organizations. So One to One to Many
    # Can a user have different roles dependend on for example project? initial not good idea.
    user_id = Column("user_id", ForeignKey("users.user_id"), primary_key=True)
    role_id = Column("role_id", ForeignKey("roles.role_id"), primary_key=True)
    organization_id = Column("organization_id", ForeignKey("organizations.organization_id"), primary_key=True)

    def __repr__(self):
        # Fstrings are better ?
        # https://realpython.com/python-f-strings/
        return(f"Pdm User Role Organization Association Table(user_id={self.user_id!r}, role_id={self.role_id!r}), organization_id={self.organization_id!r})")
