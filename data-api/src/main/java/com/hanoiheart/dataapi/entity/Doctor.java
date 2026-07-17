package com.hanoiheart.dataapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

/**
 * Bác sĩ. {@code code} is a stable business code derived from full name (slug)
 * so duplicate inserts can be idempotent across migrations.
 */
@Entity
@Table(name = "doctors", schema = "hospital")
public class Doctor extends BaseEntity {

    @Column(name = "code", nullable = false, unique = true, length = 128)
    private String code;

    @Column(name = "full_name", nullable = false)
    private String fullName;

    /** Degree prefix: TS.BS, ThS.BS, BSCKII, BSCKI, BSNT, BS. */
    @Column(name = "degree", length = 16)
    private String degree;

    @Column(name = "title")
    private String title;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id")
    private Department department;

    @Column(name = "bio")
    private String bio;

    @Column(name = "avatar_url")
    private String avatarUrl;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive = Boolean.TRUE;

    public String getCode() { return code; }
    public void setCode(String c) { this.code = c; }
    public String getFullName() { return fullName; }
    public void setFullName(String n) { this.fullName = n; }
    public String getDegree() { return degree; }
    public void setDegree(String d) { this.degree = d; }
    public String getTitle() { return title; }
    public void setTitle(String t) { this.title = t; }
    public Department getDepartment() { return department; }
    public void setDepartment(Department d) { this.department = d; }
    public String getBio() { return bio; }
    public void setBio(String b) { this.bio = b; }
    public String getAvatarUrl() { return avatarUrl; }
    public void setAvatarUrl(String a) { this.avatarUrl = a; }
    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean a) { this.isActive = a; }
}
