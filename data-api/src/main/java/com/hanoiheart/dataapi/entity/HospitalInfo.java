package com.hanoiheart.dataapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

/**
 * Hospital general info (single-row master record).
 */
@Entity
@Table(name = "hospital_info", schema = "hospital")
public class HospitalInfo extends BaseEntity {

    @Column(name = "name", nullable = false)
    private String name;

    @Column(name = "short_name")
    private String shortName;

    @Column(name = "name_en")
    private String nameEn;

    @Column(name = "slogan")
    private String slogan;

    /** JSON array, e.g. [{"label":"Cơ sở 1","address":"...","phone":"..."}]. */
    @Column(name = "addresses", columnDefinition = "jsonb")
    private String addresses;

    @Column(name = "hotline")
    private String hotline;

    /** JSON object, e.g. {"weekday":"7:30-16:30", ...}. */
    @Column(name = "working_hours", columnDefinition = "jsonb")
    private String workingHours;

    @Column(name = "grade")
    private String grade;

    @Column(name = "established_year")
    private Integer establishedYear;

    @Column(name = "website")
    private String website;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getShortName() { return shortName; }
    public void setShortName(String s) { this.shortName = s; }
    public String getNameEn() { return nameEn; }
    public void setNameEn(String n) { this.nameEn = n; }
    public String getSlogan() { return slogan; }
    public void setSlogan(String s) { this.slogan = s; }
    public String getAddresses() { return addresses; }
    public void setAddresses(String a) { this.addresses = a; }
    public String getHotline() { return hotline; }
    public void setHotline(String h) { this.hotline = h; }
    public String getWorkingHours() { return workingHours; }
    public void setWorkingHours(String w) { this.workingHours = w; }
    public String getGrade() { return grade; }
    public void setGrade(String g) { this.grade = g; }
    public Integer getEstablishedYear() { return establishedYear; }
    public void setEstablishedYear(Integer y) { this.establishedYear = y; }
    public String getWebsite() { return website; }
    public void setWebsite(String w) { this.website = w; }
}
