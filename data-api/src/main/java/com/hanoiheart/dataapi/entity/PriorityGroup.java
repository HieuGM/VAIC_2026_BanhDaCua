package com.hanoiheart.dataapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

/**
 * Đối tượng ưu tiên theo QĐ154/2024 của Bệnh viện Tim Hà Nội.
 * Roster not yet provided by domain owners (see data gap notes).
 */
@Entity
@Table(name = "priority_groups", schema = "hospital")
public class PriorityGroup extends BaseEntity {

    @Column(name = "code", nullable = false, unique = true, length = 64)
    private String code;

    @Column(name = "name", nullable = false)
    private String name;

    @Column(name = "description", columnDefinition = "text")
    private String description;

    @Column(name = "sort_order")
    private Integer sortOrder;

    public String getCode() { return code; }
    public void setCode(String c) { this.code = c; }
    public String getName() { return name; }
    public void setName(String n) { this.name = n; }
    public String getDescription() { return description; }
    public void setDescription(String d) { this.description = d; }
    public Integer getSortOrder() { return sortOrder; }
    public void setSortOrder(Integer s) { this.sortOrder = s; }
}
