package com.hanoiheart.dataapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

/**
 * Dịch vụ kỹ thuật (khám, XN, thủ thuật, CĐHA, CNT, CLVT, can thiệp TM).
 */
@Entity
@Table(name = "services", schema = "hospital")
public class HospitalService extends BaseEntity {

    @Column(name = "code", length = 64)
    private String code;

    @Column(name = "name", nullable = false)
    private String name;

    /** consultation | lab | imaging | procedure | mri | ct | intervention. */
    @Column(name = "category", length = 32)
    private String category;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id")
    private Department department;

    @Column(name = "description")
    private String description;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive = Boolean.TRUE;

    public String getCode() { return code; }
    public void setCode(String c) { this.code = c; }
    public String getName() { return name; }
    public void setName(String n) { this.name = n; }
    public String getCategory() { return category; }
    public void setCategory(String c) { this.category = c; }
    public Department getDepartment() { return department; }
    public void setDepartment(Department d) { this.department = d; }
    public String getDescription() { return description; }
    public void setDescription(String d) { this.description = d; }
    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean a) { this.isActive = a; }
}
