package com.hanoiheart.dataapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

/**
 * Chuyên khoa / khu khám (department or exam-area).
 */
@Entity
@Table(name = "departments", schema = "hospital")
public class Department extends BaseEntity {

    @Column(name = "code", nullable = false, unique = true, length = 64)
    private String code;

    @Column(name = "name", nullable = false)
    private String name;

    @Column(name = "name_en")
    private String nameEn;

    @Column(name = "description")
    private String description;

    @Column(name = "campus")
    private String campus;

    @Column(name = "floor")
    private String floor;

    @Column(name = "working_hours", columnDefinition = "jsonb")
    private String workingHours;

    @Column(name = "phone")
    private String phone;

    @Column(name = "sort_order")
    private Integer sortOrder;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive = Boolean.TRUE;

    public String getCode() { return code; }
    public void setCode(String c) { this.code = c; }
    public String getName() { return name; }
    public void setName(String n) { this.name = n; }
    public String getNameEn() { return nameEn; }
    public void setNameEn(String n) { this.nameEn = n; }
    public String getDescription() { return description; }
    public void setDescription(String d) { this.description = d; }
    public String getCampus() { return campus; }
    public void setCampus(String c) { this.campus = c; }
    public String getFloor() { return floor; }
    public void setFloor(String f) { this.floor = f; }
    public String getWorkingHours() { return workingHours; }
    public void setWorkingHours(String w) { this.workingHours = w; }
    public String getPhone() { return phone; }
    public void setPhone(String p) { this.phone = p; }
    public Integer getSortOrder() { return sortOrder; }
    public void setSortOrder(Integer s) { this.sortOrder = s; }
    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean a) { this.isActive = a; }
}
